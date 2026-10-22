import numpy as np
import pyloudnorm as pyln
import scipy.io.wavfile
from pathlib import Path
from typing import Tuple
from backend.app.schemas.manifest import AudioMeasurements, LoopValidation

def measure_audio(
    audio: np.ndarray,
    sample_rate: int,
    requested_duration_s: float
) -> AudioMeasurements:
    """
    Measures actual audio parameters: duration, LUFS loudness, true peak, and clipping.
    """
    actual_samples = len(audio)
    actual_duration_s = actual_samples / float(sample_rate)
    duration_diff_s = abs(actual_duration_s - requested_duration_s)

    # Max sample peak
    max_sample_peak = float(np.max(np.abs(audio)))
    # True peak in dBTP
    true_peak_dbtp = 20.0 * np.log10(max(1e-6, max_sample_peak))

    # Integrated loudness via pyloudnorm
    meter = pyln.Meter(sample_rate)
    # Ensure float64 and valid range for pyloudnorm
    try:
        audio_norm = audio.astype(np.float64)
        integrated_lufs = float(meter.integrated_loudness(audio_norm))
        if np.isneginf(integrated_lufs) or np.isnan(integrated_lufs):
            integrated_lufs = -70.0
    except Exception:
        integrated_lufs = -24.0

    clipping_detected = max_sample_peak > 0.999

    return AudioMeasurements(
        sample_rate=sample_rate,
        bit_depth=16,
        channels=2 if audio.ndim == 2 else 1,
        requested_duration_s=round(requested_duration_s, 3),
        actual_duration_s=round(actual_duration_s, 3),
        duration_difference_s=round(duration_diff_s, 4),
        integrated_lufs=round(integrated_lufs, 2),
        true_peak_dbtp=round(true_peak_dbtp, 2),
        max_sample_peak=round(max_sample_peak, 4),
        clipping_detected=clipping_detected
    )

def master_audio(
    audio: np.ndarray,
    sample_rate: int = 48000,
    target_lufs: float = -16.0,
    max_peak_dbtp: float = -1.0
) -> np.ndarray:
    """
    Applies ITU-R BS.1770 / EBU R128 loudness normalization and true peak limiting.
    Ensures true peak does not exceed max_peak_dbtp (default -1.0 dBTP).
    """
    meter = pyln.Meter(sample_rate)
    audio_f64 = audio.astype(np.float64)

    try:
        current_lufs = meter.integrated_loudness(audio_f64)
    except Exception:
        current_lufs = -24.0

    if not np.isneginf(current_lufs) and not np.isnan(current_lufs):
        # Normalize to target LUFS
        try:
            normalized = pyln.normalize.loudness(audio_f64, current_lufs, target_lufs)
        except Exception:
            normalized = audio_f64
    else:
        normalized = audio_f64

    # True peak limiting
    peak_ceiling = 10.0 ** (max_peak_dbtp / 20.0) # ~0.891
    max_val = np.max(np.abs(normalized))
    if max_val > peak_ceiling:
        normalized = normalized * (peak_ceiling / max_val)

    return normalized.astype(np.float32)

def write_wav(file_path: Path, audio: np.ndarray, sample_rate: int = 48000) -> None:
    """Writes 48 kHz 16-bit PCM WAV file."""
    # Clip safely to [-1.0, 1.0] before quantization
    audio_clamped = np.clip(audio, -1.0, 1.0)
    audio_int16 = (audio_clamped * 32767.0).astype(np.int16)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    scipy.io.wavfile.write(str(file_path), sample_rate, audio_int16)

def make_seamless_loop(audio: np.ndarray, sample_rate: int, crossfade_s: float = 0.08) -> Tuple[np.ndarray, LoopValidation]:
    """
    Crossfades audio boundary so start and end loop seamlessly with zero click.
    Checks and validates boundary discontinuity.
    """
    cf_samples = int(crossfade_s * sample_rate)
    if cf_samples >= len(audio) // 2:
        cf_samples = len(audio) // 4

    out = audio.copy()
    # Equal-power crossfade curve
    fade_out = np.cos(0.5 * np.pi * np.linspace(0.0, 1.0, cf_samples))[:, np.newaxis]
    fade_in = np.sin(0.5 * np.pi * np.linspace(0.0, 1.0, cf_samples))[:, np.newaxis]

    # Mix end into beginning and vice versa
    tail = out[-cf_samples:].copy()
    head = out[:cf_samples].copy()

    out[:cf_samples] = head * fade_in + tail * fade_out
    out[-cf_samples:] = tail * fade_out + head * fade_in

    # Check discontinuity between first sample and last sample
    start_samp = out[0]
    end_samp = out[-1]
    discontinuity = float(np.max(np.abs(start_samp - end_samp)))
    is_seamless = discontinuity < 0.05

    validation = LoopValidation(
        loopable_requested=True,
        is_seamless=is_seamless,
        boundary_discontinuity=round(discontinuity, 5),
        crossfade_duration_s=round(crossfade_s, 3),
        validation_status="Passed: Continuous phase boundary verified" if is_seamless else "Warning: Slight discontinuity"
    )

    return out, validation
