from typing import Dict, List, Tuple

# Note names to pitch class (0-11)
NOTE_TO_PITCH: Dict[str, int] = {
    "C": 0, "C#": 1, "DB": 1,
    "D": 2, "D#": 3, "EB": 3,
    "E": 4, "FB": 4, "E#": 5,
    "F": 5, "F#": 6, "GB": 6,
    "G": 7, "G#": 8, "AB": 8,
    "A": 9, "A#": 10, "BB": 10,
    "B": 11, "CB": 11, "B#": 0,
}

PITCH_TO_NOTE = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# Scale intervals from root
SCALES: Dict[str, List[int]] = {
    "major": [0, 2, 4, 5, 7, 9, 11],
    "minor": [0, 2, 3, 5, 7, 8, 10],            # Natural minor (Aeolian)
    "harmonic_minor": [0, 2, 3, 5, 7, 8, 11],
    "dorian": [0, 2, 3, 5, 7, 9, 10],
    "mixolydian": [0, 2, 4, 5, 7, 9, 10],
    "lydian": [0, 2, 4, 6, 7, 9, 11],
    "pentatonic_major": [0, 2, 4, 7, 9],
    "pentatonic_minor": [0, 3, 5, 7, 10],
    "blues": [0, 3, 5, 6, 7, 10],
}

# Common chord formulas (intervals from chord root)
CHORD_FORMULAS: Dict[str, List[int]] = {
    "maj": [0, 4, 7],
    "min": [0, 3, 7],
    "dim": [0, 3, 6],
    "aug": [0, 4, 8],
    "sus2": [0, 2, 7],
    "sus4": [0, 5, 7],
    "maj7": [0, 4, 7, 11],
    "min7": [0, 3, 7, 10],
    "dom7": [0, 4, 7, 10],
    "add9": [0, 4, 7, 14],
    "min9": [0, 3, 7, 10, 14],
}

def midi_to_freq(midi_note: int) -> float:
    """Calculates frequency in Hz for standard MIDI note (A4=69=440Hz)."""
    return 440.0 * (2.0 ** ((midi_note - 69.0) / 12.0))

def parse_key_signature(key_str: str) -> Tuple[str, str, int]:
    """
    Parses key strings like 'C major', 'A minor', 'F# dorian', 'Eb'.
    Returns (root_note, scale_type, root_pitch_class).
    """
    cleaned = key_str.strip().upper()
    parts = cleaned.split()
    
    root_raw = parts[0]
    # Extract note letters and accidental
    if len(root_raw) > 1 and root_raw[1] in ["#", "B"]:
        root_note = root_raw[:2]
    else:
        root_note = root_raw[:1]
        
    root_pitch = NOTE_TO_PITCH.get(root_note, 0)
    root_canonical = PITCH_TO_NOTE[root_pitch]
    
    scale_type = "major"
    if len(parts) > 1:
        sec = parts[1].lower()
        if "min" in sec:
            scale_type = "minor"
        elif "dor" in sec:
            scale_type = "dorian"
        elif "mixo" in sec:
            scale_type = "mixolydian"
        elif "lyd" in sec:
            scale_type = "lydian"
        elif "pent" in sec:
            scale_type = "pentatonic_major" if "maj" in sec else "pentatonic_minor"
    elif "m" in root_raw.lower() and not root_raw.upper().endswith("MAJ"):
        scale_type = "minor"
        
    return root_canonical, scale_type, root_pitch

def get_scale_notes(root_pitch: int, scale_type: str, octave_start: int = 3, octave_count: int = 3) -> List[int]:
    """Returns list of MIDI note numbers for the given scale across specified octaves."""
    intervals = SCALES.get(scale_type, SCALES["major"])
    notes = []
    for oct_idx in range(octave_count):
        oct_base = (octave_start + oct_idx + 1) * 12 + root_pitch
        for interval in intervals:
            notes.append(oct_base + interval)
    return sorted(list(set(notes)))
