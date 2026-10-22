import random
from typing import List
from backend.app.composition.drums import NoteEvent
from backend.app.composition.progressions import ChordEvent

def generate_bass(
    chord_events: List[ChordEvent],
    bpm: int,
    mood: str,
    total_duration_s: float,
    rng: random.Random
) -> List[NoteEvent]:
    """
    Generates genuine, musical bass lines matching the chord progression.
    Returns list of NoteEvents for the bass stem.
    """
    spb = 60.0 / bpm
    events: List[NoteEvent] = []
    total_bars = len(chord_events)

    for bar_idx, chord in enumerate(chord_events):
        bar_start = chord.start_time_s
        bar_duration = chord.duration_s
        
        # Determine bass root note in octave 1 or 2 (MIDI 28-47)
        root_midi = 24 + chord.root_pitch
        if root_midi < 28:
            root_midi += 12
        fifth_midi = root_midi + 7
        octave_midi = root_midi + 12

        progress_ratio = bar_idx / max(1, total_bars)
        is_outro = progress_ratio >= 0.85

        if is_outro or mood in ["ambient", "calm"]:
            # Sustained root note on beat 1
            dur = min(bar_duration, 4.0 * spb)
            events.append(NoteEvent(bar_start, dur, root_midi, 0.85, "bass"))
        elif mood in ["energetic", "corporate"]:
            # Driving 8th notes (root, root, fifth, octave, etc.)
            for step in range(8):
                t = bar_start + step * (spb / 2.0)
                if t >= bar_start + bar_duration or t >= total_duration_s:
                    break
                pitch = root_midi
                if step in [3, 7]:
                    pitch = fifth_midi
                elif step in [2, 6]:
                    pitch = octave_midi
                vel = 0.88 if step % 2 == 0 else 0.72
                events.append(NoteEvent(t, (spb / 2.0) * 0.9, pitch, vel, "bass"))
        elif mood in ["lo-fi", "playful"]:
            # Syncopated groove: beat 1, beat 2.5, beat 4
            pattern = [(0.0, root_midi, 0.85), (1.5, root_midi, 0.75), (2.5, fifth_midi, 0.8), (3.5, octave_midi, 0.7)]
            for beat_offset, pitch, vel in pattern:
                t = bar_start + beat_offset * spb
                if t < bar_start + bar_duration and t < total_duration_s:
                    events.append(NoteEvent(t, spb * 0.8, pitch, vel, "bass"))
        else:
            # Uplifting / Cinematic standard: Root on beat 1 and 3, passing tone on beat 4
            events.append(NoteEvent(bar_start, spb * 1.8, root_midi, 0.85, "bass"))
            t2 = bar_start + 2.0 * spb
            if t2 < bar_start + bar_duration and t2 < total_duration_s:
                events.append(NoteEvent(t2, spb * 1.6, fifth_midi, 0.80, "bass"))
            t3 = bar_start + 3.5 * spb
            if t3 < bar_start + bar_duration and t3 < total_duration_s:
                # Passing tone towards next chord root
                next_chord = chord_events[(bar_idx + 1) % total_bars]
                passing = 24 + next_chord.root_pitch
                while passing < 28: passing += 12
                events.append(NoteEvent(t3, spb * 0.45, passing - 1, 0.70, "bass"))

    # Natural resolution at final cadence
    final_bar = chord_events[-1]
    final_root = 24 + final_bar.root_pitch
    while final_root < 28: final_root += 12
    events.append(NoteEvent(final_bar.start_time_s, 3.0, final_root, 0.90, "bass"))

    events.sort(key=lambda e: e.time_s)
    return events
