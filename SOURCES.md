# SOURCES & LICENSING COMPLIANCE DISCLOSURE

## 1. Executive Summary
IncuBrix Music Studio was intentionally built to satisfy the strict commercial-use and zero-cost constraints of the IncuBrix Engineering Assessment. 

To ensure **100% legal eligibility for commercial distribution, monetization on video platforms (YouTube, TikTok, Instagram), and video-game distribution**, the system does **not** rely on third-party soundfonts with ambiguous or non-commercial licenses (such as soundfonts derived from Creative Commons Non-Commercial or proprietary GM sound sets).

Instead, all audio waveforms, percussive transients, Karplus-Strong string models, and polyphonic instrument voices are **synthesized algorithmically in source code** using vectorized mathematical equations in NumPy and SciPy.

---

## 2. Core Dependencies & Libraries

| Library | Version | Role in Pipeline | License | Commercial Use Eligible? | Source URL |
|---|---|---|---|---|---|
| **FastAPI** | 0.115.0 | Async HTTP web server & OpenAPI documentation | MIT | Yes | [https://github.com/fastapi/fastapi](https://github.com/fastapi/fastapi) |
| **Uvicorn** | 0.30.6 | ASGI web server implementation | BSD-3-Clause | Yes | [https://github.com/encode/uvicorn](https://github.com/encode/uvicorn) |
| **NumPy** | 2.5.2 | Vectorized oscillator generation, phase accumulation, and matrix mixing | BSD-3-Clause | Yes | [https://numpy.org/](https://numpy.org/) |
| **SciPy** | 1.17.1 | Butterworth IIR filtering, envelope smoothing, and 48kHz WAV I/O | BSD-3-Clause | Yes | [https://scipy.org/](https://scipy.org/) |
| **Pyloudnorm** | 0.2.0 | ITU-R BS.1770 / EBU R128 integrated LUFS loudness measurement | MIT | Yes | [https://github.com/csteinmetz1/pyloudnorm](https://github.com/csteinmetz1/pyloudnorm) |
| **Mido** | 1.3.3 | Standard MIDI file (SMF) compilation and track exporting | MIT | Yes | [https://github.com/mido/mido](https://github.com/mido/mido) |
| **Pydantic** | 2.9.2 | Strict schema validation, section interval checks, and serialization | MIT | Yes | [https://github.com/pydantic/pydantic](https://github.com/pydantic/pydantic) |
| **PyYAML** | 6.0.2 | OpenAPI 3.1 YAML export generation | MIT | Yes | [https://pyyaml.org/](https://pyyaml.org/) |
| **Pytest** | 9.1.1 | Automated test runner | MIT | Yes | [https://pytest.org/](https://pytest.org/) |
| **HTTPX** | 0.28.1 | Async HTTP test client | BSD-3-Clause | Yes | [https://www.python-httpx.org/](https://www.python-httpx.org/) |
| **React** | 19.0.0 | Frontend component architecture | MIT | Yes | [https://react.dev/](https://react.dev/) |
| **Vite** | 8.3.4 | Frontend compiler and development server | MIT | Yes | [https://vite.dev/](https://vite.dev/) |
| **Tailwind CSS** | 4.0.0 | Utility-first CSS styling engine | MIT | Yes | [https://tailwindcss.com/](https://tailwindcss.com/) |
| **Lucide React** | 1.16.0 | Sleek iconography | ISC | Yes | [https://lucide.dev/](https://lucide.dev/) |

---

## 3. Audio Sound Generation & Intellectual Property

### A. Drum Synthesis
- **Kick Drum**: Synthesized using a logarithmic pitch-drop oscillator ($160\text{ Hz} \to 48\text{ Hz}$) with an exponential decay envelope ($\tau = 0.12\text{s}$) plus a shaped high-frequency beater click ($4\text{ms}$).
- **Snare Drum**: Synthesized with dual-frequency body oscillators ($180\text{ Hz}$) combined with lowpass-filtered ($7\text{ kHz}$) and highpass-filtered ($800\text{ Hz}$) white noise bursts ($\tau = 0.14\text{s}$).
- **Hi-Hats**: Synthesized with metallic highpass filtered white noise bursts ($> 7.5\text{ kHz}$) with rapid decay ($25\text{ms}$ for closed, $150\text{ms}$ for open).
- **Crash Cymbal**: Multi-second metallic shimmer noise burst with exponential release ($\tau = 0.6\text{s}$).

### B. Bass Synthesis
- Dual-oscillator architecture combining a sub-bass sine wave with a warm second harmonic and an envelope-filtered saw wave, lowpass filtered at $800\text{ Hz}$.

### C. Harmony & Accompaniment
- Physical string modeling implemented via the **Karplus-Strong** algorithm with digital feedback delay line, one-pole lowpass filter, and Haas-effect stereo widening ($16\text{ms}$ phase offset).

### D. Lead Melody
- Additive multi-harmonic synthesis ($f, 2f, 3f, 4f$) with low-frequency vibrato ($5.5\text{ Hz}$, $1.5\%$ depth) and soft-knee hyperbolic tangent ($\tanh$) analog saturation.

---

## 4. Attribution & Commercial Warranty
All generated tracks and stems produced by IncuBrix Music Studio are generated dynamically from mathematical algorithms in this repository and are free of third-party proprietary claims. Users may monetize, modify, broadcast, or distribute the generated audio worldwide without paying royalties.
