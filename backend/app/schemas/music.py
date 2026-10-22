from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from backend.app.core.config import settings

class SectionItem(BaseModel):
    start_s: float = Field(..., ge=0.0, description="Start timestamp of the section in seconds.")
    mood: str = Field(..., min_length=1, max_length=100, description="Mood or structural role (e.g., intro, build-up, peak).")

class OutputConfig(BaseModel):
    sample_rate: int = Field(default=settings.SAMPLE_RATE, description="Audio sample rate (default 48000).")
    target_lufs: float = Field(default=settings.TARGET_LUFS, ge=-30.0, le=-6.0, description="Target integrated loudness in LUFS.")
    formats: List[str] = Field(default_factory=lambda: ["wav"], description="Output formats, e.g. ['wav', 'mp3'].")

class MusicJobRequest(BaseModel):
    prompt: str = Field(..., min_length=3, max_length=1000, description="Natural language music prompt.")
    duration_s: float = Field(..., ge=settings.MIN_DURATION_S, le=settings.MAX_DURATION_S, description="Duration in seconds (5 to 300).")
    sections: Optional[List[SectionItem]] = Field(default=None, description="Optional arrangement sections timeline.")
    tempo_bpm: Optional[int] = Field(default=None, ge=40, le=240, description="Tempo in beats per minute.")
    key: Optional[str] = Field(default=None, max_length=30, description="Musical key (e.g. 'C major', 'A minor').")
    loopable: bool = Field(default=False, description="Whether the audio should loop seamlessly.")
    narration_url: Optional[str] = Field(default=None, description="Optional URL to audio narration for voiceover ducking.")
    seed: Optional[int] = Field(default=None, description="Random seed for deterministic composition.")
    output: OutputConfig = Field(default_factory=OutputConfig, description="Output audio configuration.")

    @field_validator("duration_s")
    @classmethod
    def validate_duration(cls, v: float) -> float:
        if v < settings.MIN_DURATION_S or v > settings.MAX_DURATION_S:
            raise ValueError(f"Duration must be between {settings.MIN_DURATION_S} and {settings.MAX_DURATION_S} seconds.")
        return round(v, 2)

    @field_validator("sections")
    @classmethod
    def validate_sections(cls, v: Optional[List[SectionItem]], values) -> Optional[List[SectionItem]]:
        if not v:
            return v
        
        # Sort sections by start_s
        sorted_sections = sorted(v, key=lambda s: s.start_s)
        if sorted_sections[0].start_s != 0.0:
            raise ValueError("The first section must start at 0.0 seconds.")
            
        for i in range(1, len(sorted_sections)):
            diff = sorted_sections[i].start_s - sorted_sections[i-1].start_s
            if diff < 1.5:
                raise ValueError(f"Sections must be at least 1.5 seconds apart. Section {i} begins only {diff:.2f}s after previous.")

        return sorted_sections

class StemRegenerateRequest(BaseModel):
    seed: Optional[int] = Field(default=None, description="Optional new seed for stem variation.")
    custom_prompt: Optional[str] = Field(default=None, description="Optional refinement prompt for this stem.")
