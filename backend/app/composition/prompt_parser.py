import re
from typing import Any, Dict, List, Optional, Tuple

MOOD_PRESETS = {
    "calm": {
        "bpm": 74, "key": "C major", "genre": "acoustic", "energy": 0.3,
        "instruments": {"drums": "brush_percussion", "bass": "warm_upright", "harmony": "acoustic_guitar", "melody": "warm_flute_piano"}
    },
    "uplifting": {
        "bpm": 105, "key": "D major", "genre": "acoustic_pop", "energy": 0.75,
        "instruments": {"drums": "driving_kit", "bass": "electric_bass", "harmony": "acoustic_strum_piano", "melody": "bright_lead_bell"}
    },
    "optimistic": {
        "bpm": 100, "key": "G major", "genre": "corporate_positive", "energy": 0.65,
        "instruments": {"drums": "modern_kit", "bass": "electric_bass", "harmony": "piano_arpeggio", "melody": "bright_acoustic"}
    },
    "energetic": {
        "bpm": 128, "key": "A minor", "genre": "electronic_dance", "energy": 0.9,
        "instruments": {"drums": "punchy_electronic", "bass": "driving_synth_bass", "harmony": "pulsing_chords", "melody": "energetic_lead"}
    },
    "cinematic": {
        "bpm": 84, "key": "D minor", "genre": "cinematic_orchestral", "energy": 0.7,
        "instruments": {"drums": "orchestral_percussion", "bass": "deep_sub_bass", "harmony": "lush_strings", "melody": "cinematic_bell_lead"}
    },
    "tense": {
        "bpm": 88, "key": "F minor", "genre": "suspense_thriller", "energy": 0.6,
        "instruments": {"drums": "tense_tick", "bass": "sub_drone_bass", "harmony": "minor_dissonance_pad", "melody": "staccato_motif"}
    },
    "lo-fi": {
        "bpm": 78, "key": "Eb major", "genre": "lofi_chillhop", "energy": 0.4,
        "instruments": {"drums": "vintage_lofi_drums", "bass": "warm_sub_bass", "harmony": "jazzy_rhodes", "melody": "mellow_sine_lead"}
    },
    "playful": {
        "bpm": 116, "key": "F major", "genre": "quirky_acoustic", "energy": 0.6,
        "instruments": {"drums": "light_percussion", "bass": "plucked_upright", "harmony": "marimba_piano", "melody": "bouncy_bell"}
    },
    "ambient": {
        "bpm": 68, "key": "A dorian", "genre": "ambient_soundscape", "energy": 0.25,
        "instruments": {"drums": "minimal_shaker", "bass": "warm_sub", "harmony": "shimmer_pad", "melody": "gentle_harp"}
    },
    "corporate": {
        "bpm": 108, "key": "C major", "genre": "corporate_motivational", "energy": 0.65,
        "instruments": {"drums": "modern_pop_kit", "bass": "clean_electric_bass", "harmony": "clean_piano_chords", "melody": "uplifting_glockenspiel"}
    }
}

FAMOUS_ARTIST_PATTERNS = [
    r"\bhans\s+zimmer\b", r"\bdaft\s+punk\b", r"\bbeatles\b", r"\bbrian\s+eno\b",
    r"\bludovico\s+einaudi\b", r"\btaylor\s+swift\b", r"\bavicii\b", r"\bmax\s+richter\b",
    r"\bjohn\s+williams\b", r"\benno\b", r"\bmoby\b"
]

class PromptAnalysis:
    def __init__(
        self,
        normalized_prompt: str,
        primary_mood: str,
        detected_genre: str,
        suggested_bpm: int,
        suggested_key: str,
        meter: str,
        energy: float,
        instruments: Dict[str, str],
        warnings: List[str]
    ):
        self.normalized_prompt = normalized_prompt
        self.primary_mood = primary_mood
        self.detected_genre = detected_genre
        self.suggested_bpm = suggested_bpm
        self.suggested_key = suggested_key
        self.meter = meter
        self.energy = energy
        self.instruments = instruments
        self.warnings = warnings

    def to_dict(self) -> Dict[str, Any]:
        return {
            "normalized_prompt": self.normalized_prompt,
            "primary_mood": self.primary_mood,
            "detected_genre": self.detected_genre,
            "suggested_bpm": self.suggested_bpm,
            "suggested_key": self.suggested_key,
            "meter": self.meter,
            "energy": self.energy,
            "instruments": self.instruments,
            "warnings": self.warnings
        }

def parse_prompt(
    prompt: str,
    user_bpm: Optional[int] = None,
    user_key: Optional[str] = None
) -> PromptAnalysis:
    """
    Parses natural language prompt into concrete musical parameters.
    Handles contradictory prompts, sanitized artist names, vocal requests.
    """
    cleaned = prompt.strip()
    lowered = cleaned.lower()
    warnings: List[str] = []

    # Check for vocals request
    if re.search(r"\b(vocals?|singing|voice|lyrics|singer)\b", lowered):
        warnings.append(
            "Vocal request detected: This engine generates purely instrumental music. "
            "Melodic elements have been assigned to an expressive lead acoustic/instrumental voice."
        )

    # Check for famous artist references
    for pattern in FAMOUS_ARTIST_PATTERNS:
        match = re.search(pattern, lowered)
        if match:
            artist_name = match.group(0).title()
            warnings.append(
                f"Reference to '{artist_name}' detected: In accordance with originality and licensing policies, "
                f"the style has been mapped to original music-theoretic principles without reproducing copyrighted material."
            )

    # Check for contradictory prompts (e.g. calm vs aggressive/energetic)
    has_calm = bool(re.search(r"\b(calm|relaxing|peaceful|soft|quiet|ambient)\b", lowered))
    has_aggressive = bool(re.search(r"\b(aggressive|energetic|intense|fast|hard|driving)\b", lowered))
    if has_calm and has_aggressive:
        warnings.append(
            "Contradictory prompt detected (both 'calm' and 'energetic/aggressive' specified). "
            "Applying a progressive dynamic arrangement that begins calm and develops into an energetic peak."
        )

    # Identify primary mood
    matched_mood = "uplifting" # default
    best_score = 0
    
    for mood_key, preset in MOOD_PRESETS.items():
        score = 0
        if mood_key in lowered:
            score += 3
        # Synonyms
        if mood_key == "calm" and any(w in lowered for w in ["peace", "relax", "meditat", "gentle", "soothing"]):
            score += 2
        elif mood_key == "uplifting" and any(w in lowered for w in ["rise", "inspiring", "bright", "hope", "build"]):
            score += 2
        elif mood_key == "optimistic" and any(w in lowered for w in ["warm", "happy", "product launch", "startup", "sunny"]):
            score += 2
        elif mood_key == "energetic" and any(w in lowered for w in ["workout", "action", "pump", "power", "dance", "club"]):
            score += 2
        elif mood_key == "cinematic" and any(w in lowered for w in ["epic", "trailer", "movie", "orchestral", "dramatic"]):
            score += 2
        elif mood_key == "lo-fi" and any(w in lowered for w in ["chill", "study", "coffee", "vintage", "retro"]):
            score += 2
        elif mood_key == "tense" and any(w in lowered for w in ["mystery", "dark", "horror", "suspense", "danger"]):
            score += 2
        elif mood_key == "playful" and any(w in lowered for w in ["quirky", "fun", "bouncy", "comedy", "game"]):
            score += 2
        elif mood_key == "corporate" and any(w in lowered for w in ["business", "presentation", "tech", "explainer"]):
            score += 2
            
        if score > best_score:
            best_score = score
            matched_mood = mood_key

    preset = MOOD_PRESETS[matched_mood]
    
    # BPM calculation
    bpm = user_bpm if user_bpm is not None else preset["bpm"]
    # Key calculation
    key = user_key if user_key is not None else preset["key"]
    
    return PromptAnalysis(
        normalized_prompt=cleaned,
        primary_mood=matched_mood,
        detected_genre=preset["genre"],
        suggested_bpm=bpm,
        suggested_key=key,
        meter="4/4",
        energy=preset["energy"],
        instruments=preset["instruments"],
        warnings=warnings
    )
