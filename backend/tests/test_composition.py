import pytest
from backend.app.composition.engine import composition_engine
from backend.app.composition.prompt_parser import parse_prompt
from backend.app.composition.theory import parse_key_signature

PROMPTS = [
    ("Warm optimistic acoustic music for a startup product launch", "optimistic", "acoustic"),
    ("Calm, peaceful acoustic meditation music", "calm", "acoustic"),
    ("High energy electronic dance track for workout", "energetic", "electronic_dance"),
    ("Epic cinematic orchestral trailer with dramatic finish", "cinematic", "cinematic_orchestral"),
    ("Lo-fi chill study beats for coffee shop", "lo-fi", "lofi_chillhop"),
    ("Dark tense mystery thriller soundtrack", "tense", "suspense_thriller"),
    ("Playful bouncy acoustic theme for comedy game", "playful", "quirky_acoustic"),
    ("Ambient atmospheric soundscape with gentle chords", "ambient", "ambient_soundscape"),
    ("Modern corporate motivational presentation background", "corporate", "corporate_motivational"),
    ("Uplifting bright acoustic folk melody with build-up", "uplifting", "acoustic_pop"),
]

def test_ten_different_prompts_classification():
    """Verify ten meaningfully different prompts parse into distinct moods and parameters."""
    detected_moods = set()
    for prompt_text, expected_mood, expected_genre in PROMPTS:
        analysis = parse_prompt(prompt_text)
        assert analysis.primary_mood == expected_mood
        detected_moods.add(analysis.primary_mood)
        assert analysis.suggested_bpm >= 60
        assert len(analysis.suggested_key) > 0
    assert len(detected_moods) == 10

def test_seed_determinism():
    """Verify identical seeds produce 100% identical composition notes."""
    prompt = "Uplifting acoustic guitar and piano theme"
    plan1 = composition_engine.compose(prompt, 15.0, seed=12345)
    plan2 = composition_engine.compose(prompt, 15.0, seed=12345)

    assert plan1.bpm == plan2.bpm
    assert plan1.key == plan2.key
    assert len(plan1.chord_progression) == len(plan2.chord_progression)
    
    for stem in ["drums", "bass", "harmony", "melody"]:
        notes1 = plan1.stem_events[stem]
        notes2 = plan2.stem_events[stem]
        assert len(notes1) == len(notes2)
        for n1, n2 in zip(notes1, notes2):
            assert n1.time_s == n2.time_s
            assert n1.midi_note == n2.midi_note
            assert n1.velocity == n2.velocity

def test_different_seeds_produce_different_compositions():
    """Verify different seeds produce distinct musical variations."""
    prompt = "Uplifting acoustic guitar and piano theme"
    plan1 = composition_engine.compose(prompt, 15.0, seed=100)
    plan2 = composition_engine.compose(prompt, 15.0, seed=200)

    # Note pitches or timings should vary
    melody1 = [n.midi_note for n in plan1.stem_events["melody"]]
    melody2 = [n.midi_note for n in plan2.stem_events["melody"]]
    assert melody1 != melody2

def test_stem_regeneration_preserves_other_stems():
    """Verify regenerating drums preserves existing bass, harmony, and melody."""
    prompt = "Warm corporate acoustic music"
    plan = composition_engine.compose(prompt, 20.0, seed=999)
    
    original_bass = [n.midi_note for n in plan.stem_events["bass"]]
    original_harmony = [n.midi_note for n in plan.stem_events["harmony"]]
    original_melody = [n.midi_note for n in plan.stem_events["melody"]]

    # Regenerate drums
    new_drums = composition_engine.regenerate_stem(plan, "drums", new_seed=8888)
    assert len(new_drums) > 0
    # Original stems in the plan remain untouched
    assert [n.midi_note for n in plan.stem_events["bass"]] == original_bass
    assert [n.midi_note for n in plan.stem_events["harmony"]] == original_harmony
    assert [n.midi_note for n in plan.stem_events["melody"]] == original_melody
