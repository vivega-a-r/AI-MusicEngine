import random
from typing import List
from backend.app.composition.drums import NoteEvent
from backend.app.composition.progressions import ChordEvent

def generate_harmony(
    chord_events: List[ChordEvent],
    bpm: int,
    mood: str,
    total_duration_s: float,
    rng: random.Random
) -> List[NoteEvent]:
    """
    Generates genuine, musical harmony parts (piano chords, acoustic guitar arpeggios, or string pads).
    Returns list of NoteEvents for the harmony stem.
    """
    spb = 60.0 / bpm
    events: List[NoteEvent] = []
    total_bars = len(chord_events)

    for bar_idx, chord in enumerate(chord_events):
        bar_start = chord.start_time_s
        bar_duration = chord.duration_s
        
        # Voicing: spread chord notes across octave 3 and 4
        chord_notes = chord.notes # e.g. [48, 52, 55]
        # Open voicing: root in octave 3, fifth in octave 3, third in octave 4, octave root in 4
        root = chord_notes[0]
        third = chord_notes[1] if len(chord_notes) > 1 else root + 4
        fifth = chord_notes[2] if len(chord_notes) > 2 else root + 7
        
        voiced_notes = [root, fifth, third + 12]
        if len(chord_notes) > 3: # 7th
            voiced_notes.append(chord_notes[3] + 12)

        progress_ratio = bar_idx / max(1, total_bars)
        is_build = 0.25 <= progress_ratio < 0.55
        is_peak = 0.55 <= progress_ratio < 0.85

        if mood in ["ambient", "cinematic", "tense"]:
            # Lush sustained pad / strings: entire bar duration
            dur = min(bar_duration, 4.0 * spb)
            for note in voiced_notes:
                events.append(NoteEvent(bar_start, dur, note, 0.72, "harmony"))
        elif mood in ["calm", "optimistic", "lo-fi"]:
            # Acoustic guitar / piano arpeggios (8th note pattern)
            arpeggio_pattern = [0, 1, 2, 1, 0, 1, 2, 1]
            step_time = spb / 2.0
            for step, note_idx in enumerate(arpeggio_pattern):
                t = bar_start + step * step_time
                if t >= bar_start + bar_duration or t >= total_duration_s:
                    break
                pitch = voiced_notes[note_idx % len(voiced_notes)]
                vel = 0.75 if step in [0, 4] else 0.62
                events.append(NoteEvent(t, step_time * 1.5, pitch, vel, "harmony"))
        else:
            # Uplifting / Corporate / Energetic: Rhythmic chord stabs or broken chords
            chord_beats = [0.0, 1.0, 2.0, 3.0]
            if is_build or is_peak:
                # Syncopated 8th notes
                chord_beats = [0.0, 0.5, 1.5, 2.0, 2.5, 3.5]
                
            for beat in chord_beats:
                t = bar_start + beat * spb
                if t >= bar_start + bar_duration or t >= total_duration_s:
                    break
                dur = (spb * 0.75) if not is_peak else (spb * 0.45)
                for note in voiced_notes:
                    vel = 0.74 if beat % 1.0 == 0 else 0.60
                    events.append(NoteEvent(t, dur, note, vel, "harmony"))

    # Natural cadence resolution: sustained resolution chord on final bar
    final_bar = chord_events[-1]
    final_notes = final_bar.notes
    for note in final_notes:
        events.append(NoteEvent(final_bar.start_time_s, 3.5, note, 0.85, "harmony"))

    events.sort(key=lambda e: e.time_s)
    return events
