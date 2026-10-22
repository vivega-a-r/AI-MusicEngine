import numpy as np
import scipy.signal
from pathlib import Path
from typing import Optional, Tuple
from backend.app.schemas.manifest import DuckingDetails

def apply_voiceover_ducking(
    music_audio: np.ndarray,
    narration_audio: np.ndarray,
    sample_rate: int = 48000,
    reduction_db: float = 12.0,
    attack_ms: float = 40.0,
    release_ms: float = 400.0,
    speech_threshold_rms: float = 0.015
) -> Tuple[np.ndarray, DuckingDetails]:
    """
    Applies narration-aware volume ducking to music without mixing narration into the music file.
    Reduces music by reduction_db (default 12 dB) during speech segments.
    Smooths with attack and release to eliminate pumping.
    """
    num_samples = len(music_audio)
    
    # Convert narration to mono if stereo
    if narration_audio.ndim > 1:
        narration_mono = np.mean(narration_audio, axis=1)
    else:
        narration_mono = narration_audio

    # Pad or truncate narration to match music length
    if len(narration_mono) < num_samples:
        padded = np.zeros(num_samples, dtype=np.float32)
        padded[:len(narration_mono)] = narration_mono
        narration_mono = padded
    else:
        narration_mono = narration_mono[:num_samples]

    # Calculate frame RMS (20ms window)
    frame_len = int(0.02 * sample_rate)
    hop_len = int(0.01 * sample_rate)
    num_frames = (num_samples - frame_len) // hop_len + 1

    speech_mask = np.zeros(num_samples, dtype=np.float32)
    active_speech_samples = 0

    if num_frames > 0:
        squared = narration_mono ** 2
        # Moving window RMS
        window = np.ones(frame_len, dtype=np.float32) / frame_len
        rms_curve = np.sqrt(np.maximum(0.0, scipy.signal.lfilter(window, 1.0, squared)))
        
        # Binary activity detection
        is_speech = rms_curve > speech_threshold_rms
        active_speech_samples = int(np.sum(is_speech))
        speech_mask = is_speech.astype(np.float32)

    speech_detected = active_speech_samples > (0.1 * sample_rate) # At least 100ms of speech
    speech_duration_s = active_speech_samples / float(sample_rate)

    if not speech_detected:
        # No speech detected or silent narration
        details = DuckingDetails(
            applied=False,
            narration_detected_speech=False,
            speech_duration_s=0.0,
            ducking_reduction_db=0.0,
            attack_ms=attack_ms,
            release_ms=release_ms,
            message="No significant speech activity detected in narration; music level preserved without ducking."
        )
        return music_audio.copy(), details

    # Calculate target gain envelope
    # 0.0 means un-ducked (gain = 1.0), 1.0 means fully ducked (gain = reduction_linear)
    reduction_linear = 10.0 ** (-reduction_db / 20.0) # ~0.251 for 12 dB
    
    # Smooth speech mask with 1st-order IIR envelope follower
    attack_coef = np.exp(-1.0 / (attack_ms * 0.001 * sample_rate))
    release_coef = np.exp(-1.0 / (release_ms * 0.001 * sample_rate))
    
    duck_gain_curve = np.ones(num_samples, dtype=np.float32)
    current_env = 0.0
    
    for i in range(num_samples):
        target = speech_mask[i]
        if target > current_env:
            current_env = target + attack_coef * (current_env - target)
        else:
            current_env = target + release_coef * (current_env - target)
            
        # Map smoothed envelope to gain
        # current_env = 0.0 -> gain 1.0; current_env = 1.0 -> gain reduction_linear
        gain = 1.0 - current_env * (1.0 - reduction_linear)
        duck_gain_curve[i] = gain

    # Apply gain to music audio
    ducked_audio = music_audio.copy()
    if ducked_audio.ndim == 2:
        ducked_audio[:, 0] *= duck_gain_curve
        ducked_audio[:, 1] *= duck_gain_curve
    else:
        ducked_audio *= duck_gain_curve

    details = DuckingDetails(
        applied=True,
        narration_detected_speech=True,
        speech_duration_s=round(speech_duration_s, 2),
        ducking_reduction_db=reduction_db,
        attack_ms=attack_ms,
        release_ms=release_ms,
        message=f"Ducked music by {reduction_db} dB over {speech_duration_s:.1f}s of detected narration speech."
    )

    return ducked_audio.astype(np.float32), details
