import json
import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Header, HTTPException, Query, Response, status
from fastapi.responses import FileResponse, JSONResponse

from backend.app.audio.mastering import measure_audio, write_wav
from backend.app.composition.engine import composition_engine
from backend.app.core.config import settings
from backend.app.core.errors import IncuBrixAPIException
from backend.app.core.logging import correlation_id_ctx, logger
from backend.app.core.security import AuthenticatedUser, get_current_user
from backend.app.database.repository import job_repository
from backend.app.schemas.jobs import JobListResponse, JobResponse, JobResultUrls
from backend.app.schemas.manifest import MusicManifest
from backend.app.schemas.music import MusicJobRequest, StemRegenerateRequest
from backend.app.stems.manager import DEFAULT_STEM_GAINS, stem_manager
from backend.app.storage.local import storage_provider
from backend.app.workers.queue import task_queue

router = APIRouter()

@router.post(
    "/music/jobs",
    response_model=JobResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Create background music generation job"
)
async def create_music_job(
    request: MusicJobRequest,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Submits a music generation request.
    Returns HTTP 202 with job identifier.
    Supports idempotency via Idempotency-Key header.
    """
    # Check idempotency
    if idempotency_key:
        existing = job_repository.get_by_idempotency_key(idempotency_key)
        if existing:
            logger.info(f"Idempotent hit for key {idempotency_key}, returning existing job {existing.job_id}")
            return JobResponse(
                job_id=existing.job_id,
                status=existing.status,
                progress=existing.progress,
                current_stage=existing.current_stage,
                created_at=existing.created_at,
                updated_at=existing.updated_at,
                user_id=existing.user_id,
                request=MusicJobRequest(**existing.request_data),
                result_urls=JobResultUrls(**existing.result_urls) if existing.result_urls else None,
                manifest=MusicManifest(**existing.manifest_data) if existing.manifest_data else None,
                error=existing.error_data
            )

    job_id = f"job_{uuid.uuid4().hex[:12]}"
    correlation_id_ctx.set(job_id)
    
    # Create persistent job in database
    record = job_repository.create_job(
        job_id=job_id,
        user_id=current_user.user_id,
        request_data=request.model_dump(),
        idempotency_key=idempotency_key
    )

    # Enqueue in background task queue
    task_queue.enqueue_job(job_id)

    return JobResponse(
        job_id=record.job_id,
        status=record.status,
        progress=record.progress,
        current_stage=record.current_stage,
        created_at=record.created_at,
        updated_at=record.updated_at,
        user_id=record.user_id,
        request=request,
        result_urls=None,
        manifest=None,
        error=None
    )

@router.get(
    "/jobs/{job_id}",
    response_model=JobResponse,
    summary="Get job status and progress"
)
async def get_job_status(job_id: str):
    record = job_repository.get_by_id(job_id)
    if not record:
        raise IncuBrixAPIException(
            code="JOB_NOT_FOUND",
            message=f"Job with ID '{job_id}' does not exist.",
            status_code=404
        )

    return JobResponse(
        job_id=record.job_id,
        status=record.status,
        progress=record.progress,
        current_stage=record.current_stage,
        created_at=record.created_at,
        updated_at=record.updated_at,
        user_id=record.user_id,
        request=MusicJobRequest(**record.request_data),
        result_urls=JobResultUrls(**record.result_urls) if record.result_urls else None,
        manifest=MusicManifest(**record.manifest_data) if record.manifest_data else None,
        error=record.error_data
    )

@router.get(
    "/jobs/{job_id}/manifest",
    summary="Get job manifest JSON"
)
async def get_job_manifest(job_id: str):
    record = job_repository.get_by_id(job_id)
    if not record or not record.manifest_data:
        raise IncuBrixAPIException(
            code="MANIFEST_NOT_FOUND",
            message=f"Manifest for job '{job_id}' not found or not yet generated.",
            status_code=404
        )
    return record.manifest_data

@router.get(
    "/jobs/{job_id}/download",
    summary="Download master audio mix"
)
async def download_job_audio(
    job_id: str,
    format: str = Query("wav", description="Audio format to download (wav or mp3)")
):
    record = job_repository.get_by_id(job_id)
    if not record or record.status != "succeeded":
        raise IncuBrixAPIException(
            code="AUDIO_NOT_READY",
            message="Audio generation is not complete or failed.",
            status_code=404
        )

    mix_file = storage_provider.get_file_path(job_id, "mix.wav")
    if not mix_file.exists():
        raise IncuBrixAPIException(
            code="FILE_NOT_FOUND",
            message="Master audio file not found on disk.",
            status_code=404
        )

    return FileResponse(
        path=str(mix_file),
        media_type="audio/wav",
        filename=f"incubrix_{job_id}_mix.wav"
    )

@router.get(
    "/jobs/{job_id}/stems",
    summary="Get stem details and download links"
)
async def get_job_stems(job_id: str):
    record = job_repository.get_by_id(job_id)
    if not record or not record.manifest_data:
        raise IncuBrixAPIException(
            code="STEMS_NOT_READY",
            message="Job stems are not yet rendered.",
            status_code=404
        )
    return {
        "job_id": job_id,
        "stems": record.manifest_data.get("stems", [])
    }

@router.post(
    "/jobs/{job_id}/stems/{stem_name}/regenerate",
    response_model=JobResponse,
    summary="Regenerate a single instrument stem while preserving all others"
)
async def regenerate_single_stem(
    job_id: str,
    stem_name: str,
    request: StemRegenerateRequest = StemRegenerateRequest()
):
    if stem_name not in ["drums", "bass", "harmony", "melody"]:
        raise IncuBrixAPIException(
            code="INVALID_STEM_NAME",
            message=f"Invalid stem name '{stem_name}'. Must be drums, bass, harmony, or melody.",
            status_code=400
        )

    record = job_repository.get_by_id(job_id)
    if not record or record.status != "succeeded":
        raise IncuBrixAPIException(
            code="JOB_NOT_READY",
            message="Cannot regenerate stem for a job that has not completed.",
            status_code=400
        )

    job_dir = storage_provider.get_job_dir(job_id)
    req = MusicJobRequest(**record.request_data)

    # Reconstruct composition plan
    plan = composition_engine.compose(
        prompt=req.prompt,
        duration_s=req.duration_s,
        sections=req.sections,
        tempo_bpm=req.tempo_bpm,
        key=req.key,
        seed=req.seed
    )

    # Regenerate only the specified stem
    new_notes = composition_engine.regenerate_stem(plan, stem_name, new_seed=request.seed)
    plan.stem_events[stem_name] = new_notes

    # Render and update stems
    rendered_stems, stem_infos = stem_manager.render_and_save_all_stems(
        stem_events=plan.stem_events,
        duration_s=req.duration_s,
        output_dir=job_dir
    )

    # Recompute master mix
    mix_wav_path = job_dir / "mix.wav"
    mastered_mix, _ = stem_manager.recompute_mix(
        rendered_stems=rendered_stems,
        gains=DEFAULT_STEM_GAINS,
        duration_s=req.duration_s,
        output_file=mix_wav_path,
        target_lufs=req.output.target_lufs
    )

    master_measurements = measure_audio(mastered_mix, settings.SAMPLE_RATE, req.duration_s)

    # Update manifest
    manifest_dict = record.manifest_data or {}
    manifest_dict["master_measurements"] = master_measurements.model_dump()
    manifest_dict["stems"] = [s.model_dump() for s in stem_infos]
    manifest_dict["warnings"] = manifest_dict.get("warnings", []) + [f"Stem '{stem_name}' was regenerated with seed {request.seed or 'random'}."]

    # Write updated manifest to disk
    manifest_path = job_dir / "music_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_dict, f, indent=2)

    result_urls = record.result_urls or {}
    job_repository.complete_job(job_id, result_urls, manifest_dict)

    updated = job_repository.get_by_id(job_id)
    return JobResponse(
        job_id=updated.job_id,
        status=updated.status,
        progress=updated.progress,
        current_stage=f"Stem '{stem_name}' regenerated successfully",
        created_at=updated.created_at,
        updated_at=updated.updated_at,
        user_id=updated.user_id,
        request=req,
        result_urls=JobResultUrls(**updated.result_urls),
        manifest=MusicManifest(**updated.manifest_data),
        error=None
    )

@router.get(
    "/jobs",
    response_model=JobListResponse,
    summary="List generation history for authenticated user"
)
async def list_jobs(
    limit: int = Query(20, ge=1, le=100),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    records = job_repository.list_jobs(user_id=current_user.user_id, limit=limit)
    job_responses = []
    for r in records:
        job_responses.append(JobResponse(
            job_id=r.job_id,
            status=r.status,
            progress=r.progress,
            current_stage=r.current_stage,
            created_at=r.created_at,
            updated_at=r.updated_at,
            user_id=r.user_id,
            request=MusicJobRequest(**r.request_data),
            result_urls=JobResultUrls(**r.result_urls) if r.result_urls else None,
            manifest=MusicManifest(**r.manifest_data) if r.manifest_data else None,
            error=r.error_data
        ))
    return JobListResponse(total=len(job_responses), jobs=job_responses)

@router.delete(
    "/jobs/{job_id}",
    summary="Delete a job and its associated audio files"
)
async def delete_job(
    job_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    record = job_repository.get_by_id(job_id)
    if not record:
        raise IncuBrixAPIException(
            code="JOB_NOT_FOUND",
            message=f"Job '{job_id}' does not exist.",
            status_code=404
        )

    # Ownership enforcement
    if record.user_id != current_user.user_id and current_user.user_id != "admin":
        raise IncuBrixAPIException(
            code="FORBIDDEN",
            message="You do not have permission to delete this job.",
            status_code=403
        )

    storage_provider.delete_job_files(job_id)
    job_repository.delete_job(job_id)
    return {"message": f"Job '{job_id}' and all associated files deleted successfully."}
