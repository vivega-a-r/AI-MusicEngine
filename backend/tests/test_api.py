import time
import uuid
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_and_readiness_endpoints():
    """Verify GET /health and GET /ready endpoints return 200 OK."""
    health_res = client.get("/health")
    assert health_res.status_code == 200
    assert health_res.json()["status"] == "healthy"

    ready_res = client.get("/ready")
    assert ready_res.status_code == 200
    assert ready_res.json()["status"] == "ready"

def test_music_job_lifecycle_and_idempotency():
    """
    Verify complete job lifecycle:
    1. POST /api/v1/music/jobs with Idempotency-Key returns 202
    2. Repeat request with same Idempotency-Key returns identical job ID
    3. GET /api/v1/jobs/{job_id} reports real stage progress until succeeded
    4. GET /api/v1/jobs/{job_id}/manifest returns valid manifest
    5. GET /api/v1/jobs/{job_id}/stems returns 4 distinct stems
    6. GET /api/v1/jobs/{job_id}/download returns actual 48kHz WAV bytes
    """
    payload = {
        "prompt": "Warm optimistic acoustic background music for product demo",
        "duration_s": 8.0,
        "tempo_bpm": 105,
        "key": "C major",
        "loopable": False,
        "seed": 555,
        "output": {
            "sample_rate": 48000,
            "target_lufs": -16.0,
            "formats": ["wav"]
        }
    }
    unique_key = f"test-key-{uuid.uuid4().hex[:8]}"
    headers = {
        "Idempotency-Key": unique_key,
        "X-User-Id": "test_creator_1"
    }

    # 1. Create job
    res1 = client.post("/api/v1/music/jobs", json=payload, headers=headers)
    assert res1.status_code == 202
    data1 = res1.json()
    job_id = data1["job_id"]
    assert job_id.startswith("job_")
    assert data1["status"] in ["queued", "running"]

    # 2. Idempotency check: repeated request returns same job
    res2 = client.post("/api/v1/music/jobs", json=payload, headers=headers)
    assert res2.status_code == 202
    data2 = res2.json()
    assert data2["job_id"] == job_id

    # 3. Poll until completed (takes ~1-2 seconds)
    max_wait = 15
    start_t = time.time()
    completed = False
    
    while time.time() - start_t < max_wait:
        poll_res = client.get(f"/api/v1/jobs/{job_id}")
        assert poll_res.status_code == 200
        poll_data = poll_res.json()
        if poll_data["status"] == "succeeded":
            completed = True
            assert poll_data["progress"] == 100
            assert poll_data["result_urls"] is not None
            break
        elif poll_data["status"] == "failed":
            pytest.fail(f"Job failed unexpectedly: {poll_data.get('error')}")
        time.sleep(0.5)

    assert completed is True

    # 4. Manifest check
    manifest_res = client.get(f"/api/v1/jobs/{job_id}/manifest")
    assert manifest_res.status_code == 200
    manifest = manifest_res.json()
    assert manifest["bpm"] == 105
    assert manifest["master_measurements"]["sample_rate"] == 48000
    assert abs(manifest["master_measurements"]["actual_duration_s"] - 8.0) <= 0.05
    assert len(manifest["stems"]) == 4

    # 5. Stems check
    stems_res = client.get(f"/api/v1/jobs/{job_id}/stems")
    assert stems_res.status_code == 200
    stems_data = stems_res.json()
    stem_names = [s["name"] for s in stems_data["stems"]]
    assert set(stem_names) == {"drums", "bass", "harmony", "melody"}

    # 6. Download check: returns actual WAV bytes
    download_res = client.get(f"/api/v1/jobs/{job_id}/download")
    assert download_res.status_code == 200
    assert download_res.headers["content-type"] == "audio/wav"
    # WAV header magic number: 'RIFF'
    assert download_res.content[:4] == b"RIFF"
    assert len(download_res.content) > 10000

def test_regenerate_stem_endpoint():
    """Verify POST /api/v1/jobs/{job_id}/stems/{stem_name}/regenerate."""
    # First create and await an 8s track
    payload = {
        "prompt": "Calm acoustic guitar",
        "duration_s": 8.0,
        "seed": 888
    }
    create_res = client.post("/api/v1/music/jobs", json=payload, headers={"X-User-Id": "test_creator_1"})
    assert create_res.status_code == 202
    job_id = create_res.json()["job_id"]

    for _ in range(25):
        poll = client.get(f"/api/v1/jobs/{job_id}").json()
        if poll["status"] == "succeeded":
            break
        time.sleep(0.4)

    # Regenerate drums
    regen_res = client.post(
        f"/api/v1/jobs/{job_id}/stems/drums/regenerate",
        json={"seed": 9999}
    )
    assert regen_res.status_code == 200
    updated_data = regen_res.json()
    assert updated_data["status"] == "succeeded"
    assert "drums" in [s["name"] for s in updated_data["manifest"]["stems"]]
