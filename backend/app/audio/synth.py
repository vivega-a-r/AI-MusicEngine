import numpy as np
from typing import Dict, List, Tuple
from backend.app.audio.dsp import (
    apply_highpass_filter,
    apply_lowpass_filter,
    create_adsr_envelope,
    karplus_strong_pluck,
    stereo_widen
)
from backend.app.composition.drums import (
    MIDI_CLOSED_HAT,
    MIDI_CRASH,
    MIDI_KICK,
    MIDI_OPEN_HAT,
    MIDI_SHAKER,
    MIDI_SNARE,
    NoteEvent
)
from backend.app.composition.theory import midi_to_freq

class StemSynthesizer:
    def __init__(self, sample_rate: int = 48000):
        self.sample_rate = sample_rate

    def synthesize_drum_note(self, note: NoteEvent) -> np.ndarray:
        """Renders single drum hit to mono audio array."""
        sr = self.sample_rate
        midi = note.midi_note
        vel = note.velocity
        
        if midi == MIDI_KICK:
            # 808-style pitch-drop kick with click
            dur = 0.35
            n_samples = int(dur * sr)
            t = np.linspace(0.0, dur, n_samples, endpoint=False)
            # Exponential pitch drop from 160Hz to 48Hz
            freq_env = 48.0 + 112.0 * np.exp(-t / 0.04)
            phase = 2.0 * np.pi * np.cumsum(freq_env) / sr
            # Amplitude envelope
            amp_env = np.exp(-t / 0.12)
            # Beater click transient
            click = np.random.uniform(-1.0, 1.0, n_samples) * np.exp(-t / 0.004) * 0.4
            kick = (np.sin(phase) + click) * amp_env * vel * 0.9
            return kick.astype(np.float32)

        elif midi == MIDI_SNARE:
            # Body tone + bandpass noise
            dur = 0.28
            n_samples = int(dur * sr)
            t = np.linspace(0.0, dur, n_samples, endpoint=False)
            body = np.sin(2.0 * np.pi * 180.0 * np.exp(-t / 0.05) * t) * np.exp(-t / 0.08) * 0.5
            noise = np.random.uniform(-1.0, 1.0, n_samples) * np.exp(-t / 0.14)
            noise_filtered = apply_lowpass_filter(noise, 7000.0, sr)
            noise_filtered = apply_highpass_filter(noise_filtered, 800.0, sr)
            snare = (body + noise_filtered * 0.8) * vel * 0.85
            return snare.astype(np.float32)

        elif midi in [MIDI_CLOSED_HAT, MIDI_OPEN_HAT, MIDI_SHAKER]:
            dur = 0.06 if midi == MIDI_CLOSED_HAT else (0.18 if midi == MIDI_SHAKER else 0.32)
            n_samples = int(dur * sr)
            t = np.linspace(0.0, dur, n_samples, endpoint=False)
            noise = np.random.uniform(-1.0, 1.0, n_samples)
            # Highpass filter at 7500 Hz for crisp metallic sound
            hi_noise = apply_highpass_filter(noise, 7500.0, sr)
            decay_time = 0.025 if midi == MIDI_CLOSED_HAT else (0.08 if midi == MIDI_SHAKER else 0.15)
            env = np.exp(-t / decay_time)
            return (hi_noise * env * vel * 0.65).astype(np.float32)

        elif midi == MIDI_CRASH:
            # Long metallic shimmer cymbal
            dur = 2.2
            n_samples = int(dur * sr)
            t = np.linspace(0.0, dur, n_samples, endpoint=False)
            noise = np.random.uniform(-1.0, 1.0, n_samples)
            hi_noise = apply_highpass_filter(noise, 5500.0, sr)
            env = np.exp(-t / 0.6)
            return (hi_noise * env * vel * 0.75).astype(np.float32)
            
        else:
            # Generic percussive hit
            dur = 0.1
            n_samples = int(dur * sr)
            t = np.linspace(0.0, dur, n_samples, endpoint=False)
            hit = np.sin(2.0 * np.pi * 400.0 * t) * np.exp(-t / 0.03) * vel * 0.5
            return hit.astype(np.float32)

    def synthesize_bass_note(self, note: NoteEvent) -> np.ndarray:
        """Renders rich warm bass note with sub-sine and warm harmonics."""
        sr = self.sample_rate
        freq = midi_to_freq(note.midi_note)
        dur = max(0.1, note.duration_s)
        n_samples = int(dur * sr)
        t = np.linspace(0.0, dur, n_samples, endpoint=False)

        # Multi-oscillator: fundamental sub-sine + 2nd harmonic + filtered saw
        sub = np.sin(2.0 * np.pi * freq * t)
        harm2 = 0.4 * np.sin(4.0 * np.pi * freq * t)
        saw = 0.25 * (2.0 * (freq * t - np.floor(0.5 + freq * t)))
        
        raw_bass = sub + harm2 + saw
        # Lowpass filter for smooth bottom end
        filtered = apply_lowpass_filter(raw_bass, min(800.0, freq * 4.0), sr)
        
        # Pluck envelope: fast attack, warm sustain, gentle release
        env = create_adsr_envelope(n_samples, sr, attack_s=0.008, decay_s=0.35, sustain_level=0.7, release_s=0.08)
        return (filtered * env * note.velocity * 0.85).astype(np.float32)

    def synthesize_harmony_note(self, note: NoteEvent) -> np.ndarray:
        """Renders acoustic guitar / piano plucked note."""
        sr = self.sample_rate
        freq = midi_to_freq(note.midi_note)
        dur = max(0.1, note.duration_s)
        
        # Physical modeling Karplus-Strong string pluck
        pluck = karplus_strong_pluck(freq, dur, sr, decay=0.988)
        return (pluck * note.velocity * 0.75).astype(np.float32)

    def synthesize_melody_note(self, note: NoteEvent) -> np.ndarray:
        """Renders singing lead melody with gentle vibrato and warm acoustic presence."""
        sr = self.sample_rate
        freq = midi_to_freq(note.midi_note)
        dur = max(0.1, note.duration_s)
        n_samples = int(dur * sr)
        t = np.linspace(0.0, dur, n_samples, endpoint=False)

        # Vibrato LFO (5.5 Hz, ramps up gently after 0.1s)
        vib_ramp = np.clip((t - 0.1) * 3.0, 0.0, 1.0)
        vibrato = 1.0 + 0.015 * np.sin(2.0 * np.pi * 5.5 * t) * vib_ramp
        inst_freq = freq * vibrato
        phase = 2.0 * np.pi * np.cumsum(inst_freq) / sr

        # Rich multi-sine additive harmonics
        lead = (
            np.sin(phase) +
            0.35 * np.sin(2.0 * phase) +
            0.15 * np.sin(3.0 * phase) +
            0.08 * np.sin(4.0 * phase)
        )
        
        # Soft saturation / tape warmth
        lead = np.tanh(lead * 1.2)
        env = create_adsr_envelope(n_samples, sr, attack_s=0.03, decay_s=0.2, sustain_level=0.75, release_s=0.08)
        return (lead * env * note.velocity * 0.80).astype(np.float32)

    def render_stem(
        self,
        stem_name: str,
        note_events: List[NoteEvent],
        total_duration_s: float
    ) -> np.ndarray:
        """
        Renders all note events for a specific stem into a stereo audio buffer of exact length.
        """
        sr = self.sample_rate
        total_samples = int(round(total_duration_s * sr))
        mono_buf = np.zeros(total_samples, dtype=np.float32)

        for note in note_events:
            start_sample = int(note.time_s * sr)
            if start_sample >= total_samples:
                continue

            if stem_name == "drums":
                note_audio = self.synthesize_drum_note(note)
            elif stem_name == "bass":
                note_audio = self.synthesize_bass_note(note)
            elif stem_name == "harmony":
                note_audio = self.synthesize_harmony_note(note)
            elif stem_name == "melody":
                note_audio = self.synthesize_melody_note(note)
            else:
                note_audio = self.synthesize_harmony_note(note)

            n_samples = len(note_audio)
            end_sample = min(total_samples, start_sample + n_samples)
            copy_len = end_sample - start_sample
            if copy_len > 0:
                mono_buf[start_sample:end_sample] += note_audio[:copy_len]

        # Apply spatial stereo positioning
        if stem_name == "drums":
            stereo = np.column_stack([mono_buf, mono_buf]) # Center punch
        elif stem_name == "bass":
            stereo = np.column_stack([mono_buf, mono_buf]) # Solid center sub
        elif stem_name == "harmony":
            stereo = stereo_widen(mono_buf, sr, delay_ms=16.0) # Immersive stereo width
        elif stem_name == "melody":
            stereo = stereo_widen(mono_buf, sr, delay_ms=8.0) # Focused lead stereo
        else:
            stereo = np.column_stack([mono_buf, mono_buf])

        # Gentle natural fade-out at end (last 50ms) to ensure zero DC click
        fade_len = min(int(0.05 * sr), total_samples)
        if fade_len > 0:
            fade_curve = np.linspace(1.0, 0.0, fade_len)[:, np.newaxis]
            stereo[-fade_len:] *= fade_curve

        return stereo

def mix_stems(
    stems: Dict[str, np.ndarray],
    gains: Dict[str, float],
    total_duration_s: float,
    sample_rate: int = 48000
) -> np.ndarray:
    """
    Computes final master mix as the weighted sum of rendered stems.
    Mix = sum(stem_gain * stem_audio).
    """
    total_samples = int(round(total_duration_s * sample_rate))
    master_mix = np.zeros((total_samples, 2), dtype=np.float32)

    for stem_name, audio in stems.items():
        gain = gains.get(stem_name, 0.8)
        # Ensure audio matches length
        current_len = min(total_samples, len(audio))
        master_mix[:current_len] += audio[:current_len] * gain

    return master_mix
