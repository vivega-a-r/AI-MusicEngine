import random
import time
from typing import Any, Dict, List, Optional
from backend.app.composition.drums import NoteEvent, generate_drums
from backend.app.composition.bass import generate_bass
from backend.app.composition.harmony import generate_harmony
from backend.app.composition.melody import generate_melody
from backend.app.composition.progressions import ChordEvent, generate_progression
from backend.app.composition.prompt_parser import parse_prompt, PromptAnalysis
from backend.app.composition.theory import parse_key_signature

class CompositionPlan:
    def __init__(
        self,
        prompt_analysis: PromptAnalysis,
        bpm: int,
        key: str,
        meter: str,
        seed: int,
        duration_s: float,
        sections: List[Dict[str, Any]],
        chord_progression: List[ChordEvent],
        stem_events: Dict[str, List[NoteEvent]]
    ):
        self.prompt_analysis = prompt_analysis
        self.bpm = bpm
        self.key = key
        self.meter = meter
        self.seed = seed
        self.duration_s = duration_s
        self.sections = sections
        self.chord_progression = chord_progression
        self.stem_events = stem_events

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prompt_analysis": self.prompt_analysis.to_dict(),
            "bpm": self.bpm,
            "key": self.key,
            "meter": self.meter,
            "seed": self.seed,
            "duration_s": self.duration_s,
            "sections": self.sections,
            "chord_progression": [c.to_dict() for c in self.chord_progression],
            "stem_counts": {k: len(v) for k, v in self.stem_events.items()}
        }

class CompositionEngine:
    def compose(
        self,
        prompt: str,
        duration_s: float,
        sections: Optional[List[Any]] = None,
        tempo_bpm: Optional[int] = None,
        key: Optional[str] = None,
        loopable: bool = False,
        seed: Optional[int] = None
    ) -> CompositionPlan:
        """
        Executes deterministic, music-theory-driven procedural composition.
        Generates 4 distinct musical stems (drums, bass, harmony, melody).
        """
        # Determine seed
        actual_seed = seed if seed is not None else int(time.time() * 1000) % 1_000_000
        rng = random.Random(actual_seed)

        # Parse prompt
        analysis = parse_prompt(prompt, user_bpm=tempo_bpm, user_key=key)
        bpm = analysis.suggested_bpm
        musical_key = analysis.suggested_key
        mood = analysis.primary_mood

        # Generate chord progression
        chord_events = generate_progression(musical_key, mood, duration_s, bpm, rng)

        # Construct section timeline
        section_timeline: List[Dict[str, Any]] = []
        if sections and len(sections) > 0:
            for s in sections:
                start_val = s.start_s if hasattr(s, "start_s") else s.get("start_s", 0.0)
                mood_val = s.mood if hasattr(s, "mood") else s.get("mood", "section")
                section_timeline.append({"start_s": start_val, "mood": mood_val})
        else:
            # Automatic section arrangement based on duration
            spb = 60.0 / bpm
            bar_len = spb * 4.0
            section_timeline = [
                {"start_s": 0.0, "mood": f"{mood} intro"},
                {"start_s": round(duration_s * 0.25, 2), "mood": "build-up"},
                {"start_s": round(duration_s * 0.55, 2), "mood": "uplifting peak"},
                {"start_s": round(duration_s * 0.85, 2), "mood": "resolution cadence"},
            ]

        # Generate 4 distinct stems
        # Use sub-seeds derived from master seed for determinism
        drums_rng = random.Random(actual_seed + 101)
        bass_rng = random.Random(actual_seed + 202)
        harmony_rng = random.Random(actual_seed + 303)
        melody_rng = random.Random(actual_seed + 404)

        drums_notes = generate_drums(chord_events, bpm, mood, duration_s, drums_rng)
        bass_notes = generate_bass(chord_events, bpm, mood, duration_s, bass_rng)
        harmony_notes = generate_harmony(chord_events, bpm, mood, duration_s, harmony_rng)
        melody_notes = generate_melody(chord_events, musical_key, bpm, mood, duration_s, melody_rng)

        stem_events = {
            "drums": drums_notes,
            "bass": bass_notes,
            "harmony": harmony_notes,
            "melody": melody_notes
        }

        return CompositionPlan(
            prompt_analysis=analysis,
            bpm=bpm,
            key=musical_key,
            meter="4/4",
            seed=actual_seed,
            duration_s=duration_s,
            sections=section_timeline,
            chord_progression=chord_events,
            stem_events=stem_events
        )

    def regenerate_stem(
        self,
        existing_plan: CompositionPlan,
        stem_name: str,
        new_seed: Optional[int] = None
    ) -> List[NoteEvent]:
        """
        Regenerates a single stem while strictly preserving the existing chord progression,
        key, tempo, and timeline.
        """
        actual_seed = new_seed if new_seed is not None else existing_plan.seed + random.randint(1000, 9999)
        rng = random.Random(actual_seed)
        
        bpm = existing_plan.bpm
        mood = existing_plan.prompt_analysis.primary_mood
        duration_s = existing_plan.duration_s
        chord_events = existing_plan.chord_progression
        musical_key = existing_plan.key

        if stem_name == "drums":
            return generate_drums(chord_events, bpm, mood, duration_s, rng)
        elif stem_name == "bass":
            return generate_bass(chord_events, bpm, mood, duration_s, rng)
        elif stem_name == "harmony":
            return generate_harmony(chord_events, bpm, mood, duration_s, rng)
        elif stem_name == "melody":
            return generate_melody(chord_events, musical_key, bpm, mood, duration_s, rng)
        else:
            raise ValueError(f"Unknown stem name: '{stem_name}'. Must be drums, bass, harmony, or melody.")

composition_engine = CompositionEngine()
