import random
from typing import List
from backend.app.composition.drums import NoteEvent
from backend.app.composition.progressions import ChordEvent
from backend.app.composition.theory import get_scale_notes, parse_key_signature

def generate_melody(
    chord_events: List[ChordEvent],
    key_str: str,
    bpm: int,
    mood: str,
    total_duration_s: float,
    rng: random.Random
) -> List[NoteEvent]:
    """
    Generates genuine, musical lead melodies with motif structure, call-and-response,
    and tonic cadence resolution.
    Returns list of NoteEvents for the melody stem.
    """
    root_name, scale_type, root_pitch = parse_key_signature(key_str)
    scale_notes = get_scale_notes(root_pitch, scale_type, octave_start=4, octave_count=2)
    # Available pitches e.g. 60 to 84 (C4 to C6)
    
    spb = 60.0 / bpm
    events: List[NoteEvent] = []
    total_bars = len(chord_events)

    # 4-bar phrase motifs
    # Create an initial 4-note motif template relative to scale indices
    motif_indices = [
        rng.choice([0, 2, 4]), # Strong chord tone
        rng.choice([1, 2, 3, 5]),
        rng.choice([2, 4, 6]),
        rng.choice([4, 5, 7])
    ]

    for bar_idx, chord in enumerate(chord_events):
        bar_start = chord.start_time_s
        bar_duration = chord.duration_s
        
        progress_ratio = bar_idx / max(1, total_bars)
        is_intro = progress_ratio < 0.20
        is_build = 0.20 <= progress_ratio < 0.55
        is_peak = 0.55 <= progress_ratio < 0.85
        is_outro = progress_ratio >= 0.85

        # In ambient/lo-fi intros, melody enters gently
        if is_intro and bar_idx == 0 and mood in ["ambient", "cinematic"]:
            continue

        # Chord tone targets for this bar
        chord_midi_high = [n + 12 for n in chord.notes if (n + 12) in scale_notes]
        if not chord_midi_high:
            chord_midi_high = scale_notes

        # Rhythmic structure for melody in this bar
        # Motif variation or response
        phrase_bar = bar_idx % 4
        
        # Determine note positions in the bar
        if is_peak:
            # More active melodic runs (8th notes and dotted rhythms)
            rhythm_offsets = [0.0, 0.75, 1.5, 2.0, 3.0]
        elif is_build:
            rhythm_offsets = [0.0, 1.0, 2.0, 2.5, 3.0]
        elif mood in ["calm", "ambient"]:
            # Spacious, lyrical phrasing
            rhythm_offsets = [0.0, 2.0] if phrase_bar in [0, 2] else [1.0, 3.0]
        else:
            # Uplifting / Pop / Corporate
            rhythm_offsets = [0.0, 1.0, 2.5, 3.0] if phrase_bar % 2 == 0 else [0.5, 1.5, 2.0]

        for idx, offset in enumerate(rhythm_offsets):
            t = bar_start + offset * spb
            if t >= bar_start + bar_duration or t >= total_duration_s:
                break
                
            # Pitch selection
            # Strong beats (offset == 0.0 or 2.0) favor chord tones
            if offset in [0.0, 2.0]:
                pitch = rng.choice(chord_midi_high)
            else:
                # Use scale steps near current pitch
                base_idx = motif_indices[idx % len(motif_indices)]
                if is_peak:
                    base_idx += 2 # Higher emotional register
                clamped_idx = max(0, min(len(scale_notes) - 1, base_idx))
                pitch = scale_notes[clamped_idx]

            # Duration: lyrical sustain
            dur = spb * 0.95
            if idx == len(rhythm_offsets) - 1:
                dur = spb * 1.5 # hold phrase ending
                
            vel = 0.82 if offset in [0.0, 2.0] else 0.70
            if is_peak:
                vel += 0.08
                
            events.append(NoteEvent(t, dur, pitch, vel, "melody"))

    # Final Cadence: Resolve strictly to the tonic root note (e.g. C5 or C4) with long sustain!
    final_bar = chord_events[-1]
    tonic_midi = 60 + root_pitch
    while tonic_midi < 65:
        tonic_midi += 12
    events.append(NoteEvent(final_bar.start_time_s, 3.5, tonic_midi, 0.90, "melody"))

    events.sort(key=lambda e: e.time_s)
    return events
