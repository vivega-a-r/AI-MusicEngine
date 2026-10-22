import random
from typing import Any, Dict, List, Tuple
from backend.app.composition.progressions import ChordEvent

# General MIDI Drum Note Mapping
MIDI_KICK = 36
MIDI_SNARE = 38
MIDI_CLOSED_HAT = 42
MIDI_OPEN_HAT = 46
MIDI_CRASH = 49
MIDI_SHAKER = 70

class NoteEvent:
    def __init__(self, time_s: float, duration_s: float, midi_note: int, velocity: float, instrument_name: str = "drums"):
        self.time_s = time_s
        self.duration_s = duration_s
        self.midi_note = midi_note
        self.velocity = velocity  # 0.0 to 1.0
        self.instrument_name = instrument_name

    def to_dict(self) -> Dict[str, Any]:
        return {
            "time_s": round(self.time_s, 3),
            "duration_s": round(self.duration_s, 3),
            "midi_note": self.midi_note,
            "velocity": round(self.velocity, 2),
            "instrument_name": self.instrument_name
        }

def generate_drums(
    chord_events: List[ChordEvent],
    bpm: int,
    mood: str,
    total_duration_s: float,
    rng: random.Random
) -> List[NoteEvent]:
    """
    Generates genuine, musical drum patterns tailored to section dynamics and mood.
    Returns list of NoteEvents.
    """
    spb = 60.0 / bpm
    sp_16th = spb / 4.0
    sp_8th = spb / 2.0
    events: List[NoteEvent] = []

    total_bars = len(chord_events)
    
    for bar_idx, chord in enumerate(chord_events):
        bar_start = chord.start_time_s
        bar_duration = chord.duration_s
        
        # Section intensity: Intro, Build, Peak, Outro
        progress_ratio = bar_idx / max(1, total_bars)
        is_intro = progress_ratio < 0.25
        is_build = 0.25 <= progress_ratio < 0.55
        is_peak = 0.55 <= progress_ratio < 0.85
        is_outro = progress_ratio >= 0.85
        
        # Crash cymbal on section transitions (peak entry or first beat of project)
        if bar_idx == 0 or (is_peak and bar_idx == int(total_bars * 0.55)):
            events.append(NoteEvent(bar_start, 2.0, MIDI_CRASH, 0.85, "crash"))

        # KICK patterns
        if not is_intro or mood in ["energetic", "corporate"]:
            # Standard beats 1 and 3, or four-on-the-floor for energetic
            kick_beats = [0.0, 2.0]
            if is_peak or mood == "energetic":
                kick_beats = [0.0, 1.0, 2.0, 3.0]
            elif is_build:
                kick_beats = [0.0, 1.5, 2.0, 3.5] # syncopated
                
            for beat in kick_beats:
                t = bar_start + beat * spb
                if t < bar_start + bar_duration and t < total_duration_s:
                    vel = 0.9 if beat in [0.0, 2.0] else 0.75
                    events.append(NoteEvent(t, 0.25, MIDI_KICK, vel, "kick"))

        # SNARE patterns (typically beats 2 and 4 in 4/4)
        if not is_intro or is_build or is_peak:
            snare_beats = [1.0, 3.0]
            for beat in snare_beats:
                t = bar_start + beat * spb
                if t < bar_start + bar_duration and t < total_duration_s:
                    vel = 0.92 if is_peak else 0.8
                    events.append(NoteEvent(t, 0.2, MIDI_SNARE, vel, "snare"))
                    
            # Build-up snare rolls
            if is_build and bar_idx % 2 == 1:
                # Add 8th or 16th note pickups before next bar
                for step in range(8):
                    t = bar_start + 2.0 * spb + step * sp_16th
                    if t < bar_start + bar_duration and t < total_duration_s:
                        events.append(NoteEvent(t, 0.15, MIDI_SNARE, 0.4 + step * 0.07, "snare"))

        # HI-HAT / SHAKER patterns (8th or 16th notes)
        hat_subdivisions = 8 # 8th notes
        if mood in ["lo-fi", "ambient"]:
            hat_subdivisions = 4
        elif is_peak or mood == "energetic":
            hat_subdivisions = 16
            
        step_duration = (4.0 * spb) / hat_subdivisions
        for step in range(hat_subdivisions):
            t = bar_start + step * step_duration
            if t >= bar_start + bar_duration or t >= total_duration_s:
                break
                
            # Groove velocity accents
            is_downbeat = (step % (hat_subdivisions // 4)) == 0
            vel = 0.75 if is_downbeat else 0.55
            # Add slight micro-humanization
            vel += rng.uniform(-0.05, 0.05)
            vel = max(0.2, min(1.0, vel))
            
            note = MIDI_CLOSED_HAT
            if is_peak and step == hat_subdivisions - 1:
                note = MIDI_OPEN_HAT
                
            events.append(NoteEvent(t, 0.1, note, vel, "hihat"))

    # Musical ending cadence hit!
    final_bar = chord_events[-1]
    final_time = final_bar.start_time_s
    events.append(NoteEvent(final_time, 2.5, MIDI_CRASH, 0.88, "crash"))
    events.append(NoteEvent(final_time, 0.4, MIDI_KICK, 0.95, "kick"))

    # Sort chronologically
    events.sort(key=lambda e: e.time_s)
    return events
