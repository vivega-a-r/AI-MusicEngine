import numpy as np
import pytest
from backend.app.audio.ducking import apply_voiceover_ducking

def test_speech_ducking_applies_reduction():
    """Verify speech activity ducks music by expected ~12 dB."""
    sr = 48000
    duration_s = 5.0
    num_samples = int(duration_s * sr)
    t = np.linspace(0.0, duration_s, num_samples, endpoint=False)
    
    # Constant amplitude music
    music = np.ones((num_samples, 2), dtype=np.float32) * 0.5
    
    # Narration with speech from 1.5s to 3.5s
    narration = np.zeros(num_samples, dtype=np.float32)
    speech_start = int(1.5 * sr)
    speech_end = int(3.5 * sr)
    narration[speech_start:speech_end] = np.sin(2.0 * np.pi * 300.0 * t[speech_start:speech_end]) * 0.4
    
    ducked, details = apply_voiceover_ducking(
        music_audio=music,
        narration_audio=narration,
        sample_rate=sr,
        reduction_db=12.0
    )
    
    assert details.applied is True
    assert details.narration_detected_speech is True
    assert details.speech_duration_s >= 1.9 # Approx 2 seconds of speech
    
    # During speech (e.g. at 2.5s), level should be ~ 0.5 * 10^(-12/20) = 0.125
    mid_speech_sample = int(2.5 * sr)
    ducked_val = float(ducked[mid_speech_sample, 0])
    expected_ducked = 0.5 * (10.0 ** (-12.0 / 20.0))
    assert abs(ducked_val - expected_ducked) < 0.05
    
    # Before speech (e.g. at 0.5s), level should be near original 0.5
    pre_speech_sample = int(0.5 * sr)
    assert abs(float(ducked[pre_speech_sample, 0]) - 0.5) < 0.01

def test_silence_narration_does_not_duck():
    """Verify silent narration is detected and does not apply unnecessary ducking."""
    sr = 48000
    duration_s = 4.0
    num_samples = int(duration_s * sr)
    music = np.ones((num_samples, 2), dtype=np.float32) * 0.5
    silent_narration = np.zeros(num_samples, dtype=np.float32)
    
    ducked, details = apply_voiceover_ducking(
        music_audio=music,
        narration_audio=silent_narration,
        sample_rate=sr
    )
    
    assert details.applied is False
    assert details.narration_detected_speech is False
    assert "No significant speech activity" in details.message
    # Audio matches original
    assert np.allclose(ducked, music)
