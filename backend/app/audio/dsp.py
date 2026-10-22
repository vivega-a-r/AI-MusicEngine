import numpy as np
import scipy.signal

def create_adsr_envelope(
    num_samples: int,
    sample_rate: int,
    attack_s: float,
    decay_s: float,
    sustain_level: float,
    release_s: float
) -> np.ndarray:
    """Generates an ADSR amplitude envelope array of exact length num_samples."""
    env = np.zeros(num_samples, dtype=np.float32)
    att_samples = int(attack_s * sample_rate)
    dec_samples = int(decay_s * sample_rate)
    rel_samples = int(release_s * sample_rate)
    
    # Clamp if total duration is shorter than attack + decay
    if att_samples + dec_samples > num_samples:
        scale = num_samples / max(1, att_samples + dec_samples)
        att_samples = int(att_samples * scale)
        dec_samples = int(dec_samples * scale)
        rel_samples = min(rel_samples, num_samples - (att_samples + dec_samples))

    current_idx = 0
    # Attack
    if att_samples > 0:
        env[:att_samples] = np.linspace(0.0, 1.0, att_samples, endpoint=False)
        current_idx += att_samples
        
    # Decay
    if dec_samples > 0 and current_idx < num_samples:
        end_idx = min(num_samples, current_idx + dec_samples)
        env[current_idx:end_idx] = np.linspace(1.0, sustain_level, end_idx - current_idx, endpoint=False)
        current_idx = end_idx

    # Sustain
    sus_samples = max(0, num_samples - current_idx - rel_samples)
    if sus_samples > 0 and current_idx < num_samples:
        end_idx = min(num_samples, current_idx + sus_samples)
        env[current_idx:end_idx] = sustain_level
        current_idx = end_idx

    # Release
    if current_idx < num_samples:
        rem = num_samples - current_idx
        env[current_idx:] = np.linspace(sustain_level, 0.0, rem)

    return env

def apply_lowpass_filter(signal: np.ndarray, cutoff_hz: float, sample_rate: int, order: int = 2) -> np.ndarray:
    """Applies a Butterworth lowpass filter to audio."""
    nyquist = 0.5 * sample_rate
    normalized_cutoff = min(0.99, max(0.01, cutoff_hz / nyquist))
    b, a = scipy.signal.butter(order, normalized_cutoff, btype='low', analog=False)
    # Check if 1D or 2D
    if signal.ndim == 1:
        return scipy.signal.lfilter(b, a, signal).astype(np.float32)
    else:
        left = scipy.signal.lfilter(b, a, signal[:, 0])
        right = scipy.signal.lfilter(b, a, signal[:, 1])
        return np.column_stack([left, right]).astype(np.float32)

def apply_highpass_filter(signal: np.ndarray, cutoff_hz: float, sample_rate: int, order: int = 2) -> np.ndarray:
    """Applies a Butterworth highpass filter."""
    nyquist = 0.5 * sample_rate
    normalized_cutoff = min(0.99, max(0.01, cutoff_hz / nyquist))
    b, a = scipy.signal.butter(order, normalized_cutoff, btype='high', analog=False)
    if signal.ndim == 1:
        return scipy.signal.lfilter(b, a, signal).astype(np.float32)
    else:
        left = scipy.signal.lfilter(b, a, signal[:, 0])
        right = scipy.signal.lfilter(b, a, signal[:, 1])
        return np.column_stack([left, right]).astype(np.float32)

def karplus_strong_pluck(freq: float, duration_s: float, sample_rate: int, decay: float = 0.985) -> np.ndarray:
    """
    Physical modeling string synthesis for acoustic guitar / harp / plucks.
    """
    num_samples = int(duration_s * sample_rate)
    period = int(sample_rate / max(20.0, freq))
    if period <= 1:
        period = 2
        
    out = np.zeros(num_samples, dtype=np.float32)
    # White noise excitation burst for string pluck
    ring_buf = np.random.uniform(-1.0, 1.0, period).astype(np.float32)
    
    buf_idx = 0
    prev_sample = 0.0
    for i in range(num_samples):
        curr_sample = ring_buf[buf_idx]
        # Lowpass filter in feedback loop
        filtered = 0.5 * (curr_sample + prev_sample) * decay
        ring_buf[buf_idx] = filtered
        prev_sample = curr_sample
        out[i] = curr_sample
        buf_idx = (buf_idx + 1) % period
        
    # Apply fast fade-in to prevent DC offset clicks
    fade_len = min(64, num_samples)
    out[:fade_len] *= np.linspace(0.0, 1.0, fade_len)
    return out

def stereo_widen(mono_signal: np.ndarray, sample_rate: int, delay_ms: float = 12.0) -> np.ndarray:
    """
    Produces a 3D stereo image from mono audio using Haas effect and slight EQ tilt.
    """
    delay_samples = int((delay_ms / 1000.0) * sample_rate)
    num_samples = len(mono_signal)
    
    left = mono_signal.copy()
    right = np.zeros(num_samples, dtype=np.float32)
    if delay_samples < num_samples:
        right[delay_samples:] = mono_signal[:-delay_samples]
        
    return np.column_stack([left, right]).astype(np.float32)
