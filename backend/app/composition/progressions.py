import random
from typing import Any, Dict, List, Tuple
from backend.app.composition.theory import (
    CHORD_FORMULAS, NOTE_TO_PITCH, PITCH_TO_NOTE, SCALES, parse_key_signature
)

PROGRESSION_TEMPLATES = {
    "calm": [
        ["I", "vi", "IV", "V"],
        ["I", "IV", "vi", "IV"],
        ["I", "V", "IV", "I"],
    ],
    "uplifting": [
        ["I", "V", "vi", "IV"],
        ["I", "IV", "I", "V"],
        ["vi", "IV", "I", "V"],
    ],
    "optimistic": [
        ["I", "V", "vi", "IV"],
        ["I", "IV", "V", "I"],
        ["I", "ii", "IV", "V"],
    ],
    "energetic": [
        ["i", "VI", "III", "VII"],
        ["i", "iv", "VI", "VII"],
        ["i", "VI", "VII", "i"],
    ],
    "cinematic": [
        ["i", "VI", "III", "VII"],
        ["i", "iv", "v", "i"],
        ["i", "VI", "iv", "V"],
    ],
    "tense": [
        ["i", "bII", "i", "V"],
        ["i", "dim", "i", "VI"],
        ["i", "VI", "vii°", "i"],
    ],
    "lo-fi": [
        ["ii7", "V7", "Imaj7", "vi7"],
        ["Imaj7", "IVmaj7", "iii7", "vi7"],
        ["ii7", "V7", "Imaj7", "Imaj7"],
    ],
    "ambient": [
        ["I", "IV", "I", "V"],
        ["i", "VII", "VI", "VII"],
        ["I", "vi", "I", "IV"],
    ],
    "corporate": [
        ["I", "V", "vi", "IV"],
        ["I", "IV", "vi", "V"],
        ["IV", "I", "V", "vi"],
    ],
    "playful": [
        ["I", "V", "vi", "IV"],
        ["I", "ii", "V", "I"],
        ["I", "IV", "I", "V"],
    ]
}

ROMAN_NUMERAL_MAP = {
    # Major scale degrees (root pitch class offset, quality)
    "I": (0, "maj"), "ii": (2, "min"), "iii": (4, "min"), "IV": (5, "maj"),
    "V": (7, "maj"), "vi": (9, "min"), "vii°": (11, "dim"),
    "Imaj7": (0, "maj7"), "ii7": (2, "min7"), "iii7": (4, "min7"),
    "IVmaj7": (5, "maj7"), "V7": (7, "dom7"), "vi7": (9, "min7"),
    # Minor scale degrees
    "i": (0, "min"), "bII": (1, "maj"), "III": (3, "maj"), "iv": (5, "min"),
    "v": (7, "min"), "VI": (8, "maj"), "VII": (10, "maj"), "dim": (2, "dim"),
}

class ChordEvent:
    def __init__(
        self,
        name: str,
        root_pitch: int,
        quality: str,
        start_time_s: float,
        duration_s: float,
        notes: List[int],
        bar_index: int
    ):
        self.name = name
        self.root_pitch = root_pitch
        self.quality = quality
        self.start_time_s = start_time_s
        self.duration_s = duration_s
        self.notes = notes
        self.bar_index = bar_index

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "root_pitch": self.root_pitch,
            "quality": self.quality,
            "start_time_s": round(self.start_time_s, 3),
            "duration_s": round(self.duration_s, 3),
            "notes": self.notes,
            "bar_index": self.bar_index
        }

def build_chord_notes(root_pitch: int, quality: str, base_octave: int = 3) -> List[int]:
    """Generates MIDI note numbers for a chord with voice leading."""
    formula = CHORD_FORMULAS.get(quality, [0, 4, 7])
    base_midi = (base_octave + 1) * 12 + root_pitch
    notes = [base_midi + interval for interval in formula]
    return notes

def generate_progression(
    key_str: str,
    mood: str,
    total_duration_s: float,
    bpm: int,
    rng: random.Random
) -> List[ChordEvent]:
    """
    Generates a structured chord progression timeline for the exact duration.
    Ensures a musical cadence / resolution at the end.
    """
    root_name, scale_type, root_pitch = parse_key_signature(key_str)
    
    # Seconds per beat and seconds per 4/4 bar
    seconds_per_beat = 60.0 / bpm
    seconds_per_bar = seconds_per_beat * 4.0
    
    total_bars = max(2, int(total_duration_s / seconds_per_bar))
    # Pick progression template
    templates = PROGRESSION_TEMPLATES.get(mood, PROGRESSION_TEMPLATES["uplifting"])
    roman_prog = rng.choice(templates)
    
    chord_events: List[ChordEvent] = []
    
    for bar_idx in range(total_bars):
        start_t = bar_idx * seconds_per_bar
        # If this is the final bar, resolve to tonic (I or i) for a natural cadence!
        if bar_idx == total_bars - 1:
            rn = "I" if scale_type == "major" else "i"
        else:
            rn = roman_prog[bar_idx % len(roman_prog)]
            
        semitone_offset, quality = ROMAN_NUMERAL_MAP.get(rn, (0, "maj"))
        chord_root_pitch = (root_pitch + semitone_offset) % 12
        chord_root_name = PITCH_TO_NOTE[chord_root_pitch]
        chord_name = f"{chord_root_name}{quality}"
        
        # Calculate bar duration (cap if final partial bar)
        dur = min(seconds_per_bar, total_duration_s - start_t)
        notes = build_chord_notes(chord_root_pitch, quality, base_octave=3)
        
        chord_events.append(ChordEvent(
            name=chord_name,
            root_pitch=chord_root_pitch,
            quality=quality,
            start_time_s=start_t,
            duration_s=dur,
            notes=notes,
            bar_index=bar_idx
        ))
        
    return chord_events
