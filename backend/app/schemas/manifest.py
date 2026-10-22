from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class AudioMeasurements(BaseModel):
    sample_rate: int
    bit_depth: int
    channels: int
    requested_duration_s: float
    actual_duration_s: float
    duration_difference_s: float
    integrated_lufs: float
    true_peak_dbtp: float
    max_sample_peak: float
    clipping_detected: bool

class StemInfo(BaseModel):
    name: str
    file_path: str
    download_url: str
    gain: float
    duration_s: float
    duration_diff_s: float
    sample_rate: int
    lufs: float
    true_peak_dbtp: float

class DuckingDetails(BaseModel):
    applied: bool
    narration_detected_speech: bool
    speech_duration_s: float
    ducking_reduction_db: float
    attack_ms: float
    release_ms: float
    message: str

class LoopValidation(BaseModel):
    loopable_requested: bool
    is_seamless: bool
    boundary_discontinuity: float
    crossfade_duration_s: float
    validation_status: str

class MusicManifest(BaseModel):
    manifest_version: str = "1.0.0"
    job_id: str
    created_at: str
    user_id: str
    
    # Original Request & Interpreted Musical Parameters
    original_prompt: str
    normalized_prompt: str
    musical_parameters: Dict[str, Any]
    
    # Music Theory Breakdown
    bpm: int
    meter: str
    key: str
    scale: str
    seed: int
    chord_progression: List[str]
    section_timeline: List[Dict[str, Any]]
    
    # Measurements
    master_measurements: AudioMeasurements
    stems: List[StemInfo]
    
    # Processing Details & Performance
    composition_method: str
    rendering_engine: str
    libraries_used: Dict[str, str]
    processing_time_s: float
    cost_estimate_usd: float
    cost_explanation: str
    
    # Compliance & Labels
    instrumental_output: bool = True
    ai_generation_label: str
    license_info: Dict[str, Any]
    
    # Features
    narration_ducking: Optional[DuckingDetails] = None
    loop_validation: Optional[LoopValidation] = None
    
    # Warnings & Validation
    warnings: List[str] = Field(default_factory=list)
    validation_passed: bool = True
