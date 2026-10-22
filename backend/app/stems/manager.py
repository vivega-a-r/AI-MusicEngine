import os
import shutil
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
from backend.app.audio.mastering import master_audio, measure_audio, write_wav
from backend.app.audio.synth import StemSynthesizer, mix_stems
from backend.app.composition.drums import NoteEvent
from backend.app.schemas.manifest import StemInfo

DEFAULT_STEM_GAINS = {
    "drums": 0.85,
    "bass": 0.90,
    "harmony": 0.75,
    "melody": 0.80
}

class StemManager:
    def __init__(self, sample_rate: int = 48000):
        self.sample_rate = sample_rate
        self.synth = StemSynthesizer(sample_rate=sample_rate)

    def render_and_save_all_stems(
        self,
        stem_events: Dict[str, List[NoteEvent]],
        duration_s: float,
        output_dir: Path,
        base_url: str = "/audio"
    ) -> Tuple[Dict[str, np.ndarray], List[StemInfo]]:
        """
        Renders all stems, saves them to disk, and computes stem metrics.
        """
        stems_dir = output_dir / "stems"
        stems_dir.mkdir(parents=True, exist_ok=True)
        
        rendered_audio: Dict[str, np.ndarray] = {}
        stem_infos: List[StemInfo] = []

        for stem_name, events in stem_events.items():
            # Render stem
            audio = self.synth.render_stem(stem_name, events, duration_s)
            rendered_audio[stem_name] = audio
            
            # Save stem WAV
            stem_file = stems_dir / f"{stem_name}.wav"
            write_wav(stem_file, audio, self.sample_rate)
            
            # Measure stem
            measurement = measure_audio(audio, self.sample_rate, duration_s)
            gain = DEFAULT_STEM_GAINS.get(stem_name, 0.8)
            rel_url = f"{base_url}/{output_dir.name}/stems/{stem_name}.wav"
            
            stem_infos.append(StemInfo(
                name=stem_name,
                file_path=str(stem_file),
                download_url=rel_url,
                gain=gain,
                duration_s=measurement.actual_duration_s,
                duration_diff_s=measurement.duration_difference_s,
                sample_rate=self.sample_rate,
                lufs=measurement.integrated_lufs,
                true_peak_dbtp=measurement.true_peak_dbtp
            ))

        return rendered_audio, stem_infos

    def recompute_mix(
        self,
        rendered_stems: Dict[str, np.ndarray],
        gains: Dict[str, float],
        duration_s: float,
        output_file: Path,
        target_lufs: float = -16.0
    ) -> Tuple[np.ndarray, Path]:
        """Recomputes master mix from current stems and applies mastering."""
        raw_mix = mix_stems(rendered_stems, gains, duration_s, self.sample_rate)
        mastered = master_audio(raw_mix, self.sample_rate, target_lufs=target_lufs)
        write_wav(output_file, mastered, self.sample_rate)
        return mastered, output_file

stem_manager = StemManager()
