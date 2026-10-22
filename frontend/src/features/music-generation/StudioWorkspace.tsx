import { useState } from 'react';
import { 
  Sparkles, Sliders, Clock, Repeat, Dices, Plus, Trash2, 
  Mic, AlertCircle 
} from 'lucide-react';
import type { MusicJobRequest, SectionItem } from '../../types';

interface StudioWorkspaceProps {
  onGenerate: (request: MusicJobRequest) => void;
  isGenerating: boolean;
}

const PRESET_PROMPTS = [
  { label: '🚀 Startup Launch', prompt: 'Warm, optimistic acoustic instrumental music with an uplifting finish', duration: 45, bpm: 100, key: 'C major' },
  { label: '🎬 Cinematic Trailer', prompt: 'Epic cinematic orchestral trailer with building percussion and dramatic cadence', duration: 30, bpm: 84, key: 'D minor' },
  { label: '☕ Lo-Fi Study', prompt: 'Chill lo-fi study beats with warm electric keys and mellow groove', duration: 24, bpm: 78, key: 'Eb major' },
  { label: '⚡ Workout Energy', prompt: 'Driving energetic dance workout track with punchy drums and synth bass', duration: 20, bpm: 128, key: 'A minor' },
  { label: '🧘 Calm Meditation', prompt: 'Peaceful soothing acoustic guitar and warm upright bass for wellness video', duration: 15, bpm: 72, key: 'C major' },
];

const MOODS = ['calm', 'uplifting', 'optimistic', 'energetic', 'cinematic', 'tense', 'lo-fi', 'playful', 'ambient', 'corporate'];
const KEYS = ['C major', 'G major', 'D major', 'A major', 'E major', 'F major', 'A minor', 'D minor', 'E minor', 'B minor', 'Eb major', 'A dorian'];

export const StudioWorkspace: React.FC<StudioWorkspaceProps> = ({ onGenerate, isGenerating }) => {
  const [prompt, setPrompt] = useState('Warm, optimistic acoustic instrumental music with an uplifting finish');
  const [duration, setDuration] = useState(45);
  const [tempo, setTempo] = useState<number | ''>(100);
  const [key, setKey] = useState('C major');
  const [loopable, setLoopable] = useState(false);
  const [seed, setSeed] = useState<number | ''>(42);
  const [targetLufs, setTargetLufs] = useState(-16);
  const [narrationUrl, setNarrationUrl] = useState('');
  const [enableNarration, setEnableNarration] = useState(false);
  
  // Dynamic sections
  const [sections, setSections] = useState<SectionItem[]>([
    { start_s: 0.0, mood: 'calm intro' },
    { start_s: 12.5, mood: 'build-up' },
    { start_s: 30.0, mood: 'uplifting peak' },
  ]);

  const [validationError, setValidationError] = useState<string | null>(null);

  const applyPreset = (preset: typeof PRESET_PROMPTS[0]) => {
    setPrompt(preset.prompt);
    setDuration(preset.duration);
    setTempo(preset.bpm);
    setKey(preset.key);
    // Auto adjust sections for duration
    setSections([
      { start_s: 0.0, mood: 'intro' },
      { start_s: Math.round(preset.duration * 0.25 * 10) / 10, mood: 'build-up' },
      { start_s: Math.round(preset.duration * 0.65 * 10) / 10, mood: 'peak' },
    ]);
  };

  const handleRandomSeed = () => {
    setSeed(Math.floor(Math.random() * 900000) + 100000);
  };

  const addSection = () => {
    const lastSection = sections[sections.length - 1];
    const newStart = lastSection ? Math.min(duration - 2, lastSection.start_s + 4.0) : 0.0;
    if (newStart >= duration) {
      setValidationError("Cannot add section past the requested duration.");
      return;
    }
    setSections([...sections, { start_s: Math.round(newStart * 10) / 10, mood: 'transition' }]);
    setValidationError(null);
  };

  const removeSection = (idx: number) => {
    if (sections.length <= 1) {
      setValidationError("At least one arrangement section is required.");
      return;
    }
    setSections(sections.filter((_: SectionItem, i: number) => i !== idx));
    setValidationError(null);
  };

  const updateSection = (idx: number, field: keyof SectionItem, value: any) => {
    const updated = [...sections];
    updated[idx] = { ...updated[idx], [field]: value };
    setSections(updated);
  };

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setValidationError(null);

    // Validation
    if (!prompt.trim() || prompt.trim().length < 3) {
      setValidationError("Please enter a descriptive prompt with at least 3 characters.");
      return;
    }

    if (duration < 5.0 || duration > 300.0) {
      setValidationError("Duration must be between 5 and 300 seconds.");
      return;
    }

    // Validate sections
    const sortedSections = [...sections].sort((a, b) => a.start_s - b.start_s);
    if (sortedSections[0].start_s !== 0.0) {
      setValidationError("The first section must start at 0.0 seconds.");
      return;
    }

    for (let i = 1; i < sortedSections.length; i++) {
      if (sortedSections[i].start_s - sortedSections[i - 1].start_s < 1.5) {
        setValidationError(`Sections must be at least 1.5 seconds apart. Section ${i + 1} starts too close to previous.`);
        return;
      }
      if (sortedSections[i].start_s >= duration) {
        setValidationError(`Section starts at ${sortedSections[i].start_s}s which exceeds total duration of ${duration}s.`);
        return;
      }
    }

    const payload: MusicJobRequest = {
      prompt: prompt.trim(),
      duration_s: duration,
      sections: sortedSections,
      tempo_bpm: tempo === '' ? undefined : Number(tempo),
      key: key || undefined,
      loopable,
      seed: seed === '' ? undefined : Number(seed),
      narration_url: enableNarration && narrationUrl.trim() ? narrationUrl.trim() : undefined,
      output: {
        sample_rate: 48000,
        target_lufs: targetLufs,
        formats: ['wav'],
      },
    };

    onGenerate(payload);
  };

  return (
    <div className="w-full max-w-5xl mx-auto space-y-6">
      {/* Preset Quick Chips */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
        <span className="text-xs font-semibold text-slate-400 whitespace-nowrap mr-1">Presets:</span>
        {PRESET_PROMPTS.map((p, idx) => (
          <button
            key={idx}
            onClick={() => applyPreset(p)}
            type="button"
            className="text-xs px-3 py-1.5 rounded-full bg-slate-800/80 hover:bg-slate-700/80 text-slate-300 border border-slate-700/60 whitespace-nowrap transition-colors flex items-center gap-1.5"
          >
            <span>{p.label}</span>
          </button>
        ))}
      </div>

      {/* Main Studio Form Card */}
      <form onSubmit={handleFormSubmit} className="bg-[#121A2B] border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-2xl space-y-6 relative">
        {/* Glow corner */}
        <div className="absolute top-0 right-0 w-64 h-64 bg-violet-600/10 rounded-full blur-3xl pointer-events-none" />

        {/* Section 1: Prompt Input */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="text-sm font-semibold text-white flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-cyan-400" />
              <span>Describe the Music You Want</span>
            </label>
            <span className="text-xs text-slate-400 font-mono">{prompt.length} / 1000</span>
          </div>

          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            rows={3}
            placeholder="e.g., Warm, optimistic acoustic instrumental music for a product launch, beginning calmly and ending with an uplifting finish..."
            className="w-full bg-[#0B1020] border border-slate-700/80 rounded-2xl p-4 text-slate-100 placeholder-slate-500 text-sm focus:outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 transition-all resize-none"
          />

          {/* Quick Mood Selector Chips */}
          <div className="flex flex-wrap items-center gap-1.5 mt-2.5">
            <span className="text-[11px] text-slate-400 mr-1">Mood Tags:</span>
            {MOODS.map((m) => (
              <button
                key={m}
                type="button"
                onClick={() => {
                  if (!prompt.toLowerCase().includes(m)) {
                    setPrompt((prev: string) => prev ? `${prev}, ${m}` : m);
                  }
                }}
                className="text-[11px] px-2 py-0.5 rounded-md bg-slate-800/60 hover:bg-violet-600/20 text-slate-300 hover:text-cyan-300 border border-slate-700/50 transition-colors capitalize"
              >
                +{m}
              </button>
            ))}
          </div>
        </div>

        {/* Section 2: Duration & Composition Controls */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-2 border-t border-slate-800/80">
          {/* Duration Slider */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5 text-cyan-400" />
                <span>Exact Duration</span>
              </label>
              <div className="flex items-center gap-1 bg-[#0B1020] px-2 py-0.5 rounded-lg border border-slate-700">
                <input
                  type="number"
                  min="5"
                  max="300"
                  step="0.5"
                  value={duration}
                  onChange={(e) => setDuration(Math.max(5, Math.min(300, parseFloat(e.target.value) || 5)))}
                  className="w-12 text-xs font-mono font-bold text-cyan-300 bg-transparent text-right focus:outline-none"
                />
                <span className="text-[11px] text-slate-400">sec</span>
              </div>
            </div>

            <input
              type="range"
              min="5"
              max="180"
              step="1"
              value={duration}
              onChange={(e) => setDuration(parseInt(e.target.value))}
              className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-cyan-400"
            />
            <div className="flex justify-between text-[10px] text-slate-500 font-mono">
              <span>5s (Logo)</span>
              <span>45s (Reel)</span>
              <span>180s (Full)</span>
            </div>
          </div>

          {/* Tempo & Key */}
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-300">Tempo (BPM)</label>
              <input
                type="number"
                min="40"
                max="220"
                placeholder="Auto"
                value={tempo}
                onChange={(e) => setTempo(e.target.value ? parseInt(e.target.value) : '')}
                className="w-full bg-[#0B1020] border border-slate-700 rounded-xl px-3 py-2 text-xs font-mono text-slate-200 focus:outline-none focus:border-cyan-400"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-300">Musical Key</label>
              <select
                value={key}
                onChange={(e) => setKey(e.target.value)}
                className="w-full bg-[#0B1020] border border-slate-700 rounded-xl px-2 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-400 cursor-pointer"
              >
                {KEYS.map(k => (
                  <option key={k} value={k}>{k}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Seed & Loopable */}
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <label className="text-xs font-semibold text-slate-300">Seed</label>
                <button
                  type="button"
                  onClick={handleRandomSeed}
                  title="Randomize seed"
                  className="text-slate-400 hover:text-cyan-400 transition-colors"
                >
                  <Dices className="w-3.5 h-3.5" />
                </button>
              </div>
              <input
                type="number"
                placeholder="Deterministic"
                value={seed}
                onChange={(e) => setSeed(e.target.value ? parseInt(e.target.value) : '')}
                className="w-full bg-[#0B1020] border border-slate-700 rounded-xl px-3 py-2 text-xs font-mono text-slate-200 focus:outline-none focus:border-cyan-400"
              />
            </div>

            <div className="space-y-1.5 flex flex-col justify-end">
              <label className="text-xs font-semibold text-slate-300 flex items-center justify-between">
                <span>Seamless Loop</span>
              </label>
              <button
                type="button"
                onClick={() => setLoopable(!loopable)}
                className={`w-full py-2 px-3 rounded-xl text-xs font-semibold flex items-center justify-center gap-1.5 transition-all border ${
                  loopable
                    ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/50 shadow-sm shadow-cyan-500/20'
                    : 'bg-[#0B1020] text-slate-400 border-slate-700 hover:border-slate-600'
                }`}
              >
                <Repeat className="w-3.5 h-3.5" />
                <span>{loopable ? 'Loop On' : 'One-Shot'}</span>
              </button>
            </div>
          </div>
        </div>

        {/* Target LUFS Setting */}
        <div className="flex items-center justify-between p-3 bg-[#0B1020] rounded-xl border border-slate-800 text-xs">
          <span className="text-slate-400">Target Broadcast Loudness:</span>
          <div className="flex items-center gap-2">
            {[-14, -16, -18].map((lufs) => (
              <button
                key={lufs}
                type="button"
                onClick={() => setTargetLufs(lufs)}
                className={`px-2.5 py-1 rounded-lg text-xs font-mono font-medium transition-colors ${
                  targetLufs === lufs
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
                    : 'bg-slate-800 text-slate-400 hover:text-slate-200'
                }`}
              >
                {lufs} LUFS
              </button>
            ))}
          </div>
        </div>

        {/* Section 3: Dynamic Arrangement Sections Timeline */}
        <div className="pt-2 border-t border-slate-800/80 space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="text-xs font-semibold text-slate-200 flex items-center gap-1.5">
                <Sliders className="w-3.5 h-3.5 text-violet-400" />
                <span>Arrangement Timeline & Section Progression</span>
              </h4>
              <p className="text-[11px] text-slate-400">
                Structure your soundtrack across video milestones (Intro, Build-up, Climax, Resolution).
              </p>
            </div>

            <button
              type="button"
              onClick={addSection}
              className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-slate-300 border border-slate-700 transition-colors"
            >
              <Plus className="w-3.5 h-3.5 text-cyan-400" />
              <span>Add Section</span>
            </button>
          </div>

          {/* Section rows */}
          <div className="space-y-2">
            {sections.map((sec: SectionItem, idx: number) => (
              <div
                key={idx}
                className="flex items-center gap-3 bg-[#0B1020] border border-slate-800 rounded-xl p-2.5 text-xs"
              >
                <span className="text-[10px] font-mono text-slate-500 w-6">#{idx + 1}</span>
                <div className="flex items-center gap-1.5">
                  <span className="text-slate-400 text-[11px]">Start:</span>
                  <input
                    type="number"
                    min="0"
                    max={duration}
                    step="0.5"
                    disabled={idx === 0}
                    value={sec.start_s}
                    onChange={(e) => updateSection(idx, 'start_s', parseFloat(e.target.value) || 0)}
                    className="w-16 bg-[#121A2B] border border-slate-700 rounded-lg px-2 py-1 text-cyan-300 font-mono text-xs focus:outline-none disabled:opacity-50"
                  />
                  <span className="text-slate-500 font-mono text-[10px]">s</span>
                </div>

                <div className="flex-1 flex items-center gap-1.5">
                  <span className="text-slate-400 text-[11px]">Role:</span>
                  <input
                    type="text"
                    value={sec.mood}
                    onChange={(e) => updateSection(idx, 'mood', e.target.value)}
                    placeholder="e.g. calm intro, build-up, peak"
                    className="w-full bg-[#121A2B] border border-slate-700 rounded-lg px-3 py-1 text-slate-200 text-xs focus:outline-none focus:border-cyan-400"
                  />
                </div>

                {idx > 0 && (
                  <button
                    type="button"
                    onClick={() => removeSection(idx)}
                    className="text-slate-500 hover:text-red-400 p-1 transition-colors"
                    title="Remove section"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Section 4: Voiceover Ducking Toggle */}
        <div className="pt-2 border-t border-slate-800/80">
          <div className="flex items-center justify-between mb-2">
            <label className="text-xs font-semibold text-slate-300 flex items-center gap-1.5 cursor-pointer">
              <input
                type="checkbox"
                checked={enableNarration}
                onChange={(e) => setEnableNarration(e.target.checked)}
                className="rounded bg-slate-800 border-slate-700 text-cyan-500 focus:ring-0 mr-1"
              />
              <Mic className="w-3.5 h-3.5 text-cyan-400" />
              <span>Voiceover / Narration Aware Music Ducking</span>
            </label>
            <span className="text-[10px] text-slate-400 font-mono">12 dB attenuation</span>
          </div>

          {enableNarration && (
            <div className="p-3 bg-[#0B1020] rounded-xl border border-slate-800 space-y-2">
              <input
                type="url"
                placeholder="Enter narration audio URL (e.g. https://.../voiceover.mp3) or leave empty for test speech ducking"
                value={narrationUrl}
                onChange={(e) => setNarrationUrl(e.target.value)}
                className="w-full bg-[#121A2B] border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-400"
              />
              <p className="text-[11px] text-slate-400">
                Music is smoothly attenuated by 12 dB during spoken dialogue using envelope detection.
              </p>
            </div>
          )}
        </div>

        {/* Validation Error Message */}
        {validationError && (
          <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-xs text-red-300 flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
            <span>{validationError}</span>
          </div>
        )}

        {/* Submit Button */}
        <div className="pt-2">
          <button
            type="submit"
            disabled={isGenerating}
            className="w-full py-4 rounded-2xl bg-gradient-to-r from-violet-600 via-purple-600 to-cyan-500 hover:from-violet-500 hover:to-cyan-400 text-white font-bold text-sm sm:text-base shadow-xl shadow-violet-500/25 hover:shadow-violet-500/40 hover:scale-[1.01] active:scale-[0.99] transition-all disabled:opacity-50 flex items-center justify-center gap-2"
          >
            <Sparkles className="w-5 h-5 text-cyan-200 animate-pulse" />
            <span>{isGenerating ? 'Composing & Synthesizing Audio...' : 'Generate Original Background Music'}</span>
          </button>
          <div className="flex items-center justify-center gap-4 text-[11px] text-slate-500 mt-2">
            <span>✓ 48 kHz WAV</span>
            <span>✓ 4 Independent Stems</span>
            <span>✓ -16 LUFS Loudness</span>
            <span>✓ 100% Zero-Cost Local Engine</span>
          </div>
        </div>
      </form>
    </div>
  );
};
