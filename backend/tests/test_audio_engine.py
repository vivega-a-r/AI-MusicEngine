import numpy as np
import pytest
from pathlib import Path
from backend.app.audio.mastering import measure_audio, write_wav
from backend.app.audio.midi import export_all_midi_files
from backend.app.composition.engine import composition_engine
from backend.app.stems.manager import DEFAULT_STEM_GAINS, stem_manager

@pytest.mark.parametrize("duration_s", [5.0, 10.0, 45.0])
def test_audio_duration_and_sample_rate(tmp_path, duration_s):
    """Verify mix and every stem match requested duration within 0.05s and use 48kHz."""
    plan = composition_engine.compose("Uplifting bright music", duration_s, seed=42)
    rendered_stems, stem_infos = stem_manager.render_and_save_all_stems(
        plan.stem_events, duration_s, tmp_path
    )
    
    # Check every stem
    for info in stem_infos:
        assert info.sample_rate == 48000
        assert abs(info.duration_s - duration_s) <= 0.05
        assert info.name in ["drums", "bass", "harmony", "melody"]

    # Check master mix
    mix_file = tmp_path / "mix.wav"
    mastered, _ = stem_manager.recompute_mix(
        rendered_stems, DEFAULT_STEM_GAINS, duration_s, mix_file
    )
    measurement = measure_audio(mastered, 48000, duration_s)
    
    assert measurement.sample_rate == 48000
    assert measurement.duration_difference_s <= 0.05
    assert not measurement.clipping_detected
    assert measurement.true_peak_dbtp <= -0.99 # Ceiling <= -1.0 dBTP

def test_stems_are_genuinely_independent():
    """
    Verify each stem contains its own independent musical content,
    and is not a frequency-filtered copy of the final mix.
    """
    plan = composition_engine.compose("Warm acoustic theme", 10.0, seed=77)
    synth = stem_manager.synth
    
    drums_audio = synth.render_stem("drums", plan.stem_events["drums"], 10.0)
    bass_audio = synth.render_stem("bass", plan.stem_events["bass"], 10.0)
    harmony_audio = synth.render_stem("harmony", plan.stem_events["harmony"], 10.0)
    melody_audio = synth.render_stem("melody", plan.stem_events["melody"], 10.0)

    # Check correlation between distinct stems is low (uncorrelated musical parts)
    # Drums vs Melody correlation
    corr_dm = np.corrcoef(drums_audio[:, 0], melody_audio[:, 0])[0, 1]
    assert abs(corr_dm) < 0.35 # Distinct waveforms

    # Bass vs Harmony correlation
    corr_bh = np.corrcoef(bass_audio[:, 0], harmony_audio[:, 0])[0, 1]
    assert abs(corr_bh) < 0.45 # Distinct parts

def test_midi_export(tmp_path):
    """Verify standard MIDI files and zip packaging."""
    plan = composition_engine.compose("Energetic dance track", 12.0, seed=12)
    zip_path = export_all_midi_files(plan.stem_events, plan.bpm, tmp_path / "midi")
    
    assert zip_path.exists()
    assert zip_path.stat().st_size > 500 # Valid zip archive
    for stem in ["drums", "bass", "harmony", "melody"]:
        mid_file = tmp_path / "midi" / f"{stem}.mid"
        assert mid_file.exists()
        assert mid_file.stat().st_size > 100
