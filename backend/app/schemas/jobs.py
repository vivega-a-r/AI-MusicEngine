from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from backend.app.schemas.music import MusicJobRequest
from backend.app.schemas.manifest import MusicManifest

class JobResultUrls(BaseModel):
    mix_wav: Optional[str] = None
    mix_mp3: Optional[str] = None
    mix_ducked_wav: Optional[str] = None
    stems: Dict[str, str] = Field(default_factory=dict)
    midi_zip: Optional[str] = None
    manifest_json: Optional[str] = None

class JobResponse(BaseModel):
    job_id: str
    status: str = Field(..., description="Job status: queued, running, succeeded, failed.")
    progress: int = Field(..., ge=0, le=100, description="Real stage progress percentage.")
    current_stage: str = Field(..., description="Human-readable description of current processing stage.")
    created_at: str
    updated_at: str
    user_id: str
    request: MusicJobRequest
    result_urls: Optional[JobResultUrls] = None
    manifest: Optional[MusicManifest] = None
    error: Optional[Dict[str, Any]] = None

class JobListResponse(BaseModel):
    total: int
    jobs: List[JobResponse]
