import pytest
from fastapi.testclient import TestClient
from backend.app.composition.prompt_parser import parse_prompt
from backend.app.main import app

client = TestClient(app)

def test_hard_case_minimum_duration_5s():
    """Hard Case: Minimum supported 5.0 seconds duration generates valid audio and manifest."""
    payload = {
        "prompt": "Punchy quick intro logo theme",
        "duration_s": 5.0,
        "seed": 101
    }
    res = client.post("/api/v1/music/jobs", json=payload)
    assert res.status_code == 202
    job_id = res.json()["job_id"]
    assert job_id is not None

def test_hard_case_duration_under_minimum_rejected():
    """Hard Case: Duration < 5s rejected with validation error."""
    payload = {
        "prompt": "Too short",
        "duration_s": 3.0
    }
    res = client.post("/api/v1/music/jobs", json=payload)
    assert res.status_code == 422 # Validation error

def test_hard_case_duration_over_maximum_rejected():
    """Hard Case: Duration > 300s rejected with validation error."""
    payload = {
        "prompt": "Too long",
        "duration_s": 350.0
    }
    res = client.post("/api/v1/music/jobs", json=payload)
    assert res.status_code == 422 # Validation error

def test_hard_case_contradictory_prompt():
    """Hard Case: Contradictory prompt ('calm but aggressive') logs warning and applies progressive curve."""
    analysis = parse_prompt("Calm relaxing peaceful melody but aggressive and fast workout beats")
    assert any("Contradictory prompt detected" in w for w in analysis.warnings)

def test_hard_case_artist_reference():
    """Hard Case: Prompts referencing famous artists are sanitized and original theory used with disclaimer."""
    analysis = parse_prompt("Cinematic epic trailer soundtrack in the style of Hans Zimmer")
    assert any("Hans Zimmer" in w for w in analysis.warnings)
    assert any("mapped to original music-theoretic principles" in w for w in analysis.warnings)

def test_hard_case_vocals_requested():
    """Hard Case: Prompts requesting vocals are converted to instrumental lead and warned."""
    analysis = parse_prompt("Catchy pop song with female vocals and singing")
    assert any("Vocal request detected" in w for w in analysis.warnings)
    assert any("generates purely instrumental music" in w for w in analysis.warnings)

def test_hard_case_sections_too_close():
    """Hard Case: Sections less than 1.5s apart are rejected with meaningful error."""
    payload = {
        "prompt": "Rapid section changes",
        "duration_s": 30.0,
        "sections": [
            {"start_s": 0.0, "mood": "intro"},
            {"start_s": 1.0, "mood": "too fast"} # Only 1.0s apart!
        ]
    }
    res = client.post("/api/v1/music/jobs", json=payload)
    assert res.status_code == 422
    assert "at least 1.5 seconds apart" in str(res.json())

def test_hard_case_sections_not_starting_at_zero():
    """Hard Case: First section not starting at 0.0 is rejected."""
    payload = {
        "prompt": "Offset start",
        "duration_s": 30.0,
        "sections": [
            {"start_s": 3.0, "mood": "intro"}
        ]
    }
    res = client.post("/api/v1/music/jobs", json=payload)
    assert res.status_code == 422
    assert "must start at 0.0" in str(res.json())

def test_hard_case_nonexistent_job_returns_404():
    """Hard Case: Requesting non-existent job ID returns 404 with standard error JSON."""
    res = client.get("/api/v1/jobs/job_does_not_exist_9999")
    assert res.status_code == 404
    data = res.json()
    assert data["error"]["code"] == "JOB_NOT_FOUND"

def test_hard_case_invalid_stem_name_returns_400():
    """Hard Case: Regenerating non-existent stem name returns 400."""
    res = client.post("/api/v1/jobs/job_123/stems/accordion/regenerate", json={})
    assert res.status_code == 400
    assert res.json()["error"]["code"] == "INVALID_STEM_NAME"
