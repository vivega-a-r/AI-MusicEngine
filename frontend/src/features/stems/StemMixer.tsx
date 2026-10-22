import { useState } from 'react';
import { Sliders, RefreshCw, Download } from 'lucide-react';
import type { JobResponse } from '../../types';
import { apiService } from '../../services/api';

interface StemMixerProps {
  job: JobResponse;
  onJobUpdated: (updatedJob: JobResponse) => void;
}

export const StemMixer: React.FC<StemMixerProps> = ({ job, onJobUpdated }) => {
  const stems = job.manifest?.stems || [];
  
  // Track mute, solo, and gain state per stem
  const [mutedStems, setMutedStems] = useState<Record<string, boolean>>({});
  const [soloStem, setSoloStem] = useState<string | null>(null);
  const [stemGains, setStemGains] = useState<Record<string, number>>({
    drums: 0.85,
    bass: 0.90,
    harmony: 0.75,
    melody: 0.80,
  });
  const [regeneratingStem, setRegeneratingStem] = useState<string | null>(null);
  const [regenError, setRegenError] = useState<string | null>(null);

  const toggleMute = (stemName: string) => {
    setMutedStems((prev: Record<string, boolean>) => ({ ...prev, [stemName]: !prev[stemName] }));
  };

  const toggleSolo = (stemName: string) => {
    setSoloStem((prev: string | null) => (prev === stemName ? null : stemName));
  };

  const handleGainChange = (stemName: string, value: number) => {
    setStemGains((prev: Record<string, number>) => ({ ...prev, [stemName]: value }));
  };

  const handleRegenerateStem = async (stemName: string) => {
    try {
      setRegeneratingStem(stemName);
      setRegenError(null);
      const updated = await apiService.regenerateStem(job.job_id, stemName);
      onJobUpdated(updated);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : `Failed to regenerate ${stemName}`;
      setRegenError(msg);
    } finally {
      setRegeneratingStem(null);
    }
  };

  const getStemColor = (name: string) => {
    switch (name) {
      case 'drums': return 'from-orange-500 to-amber-400';
      case 'bass': return 'from-violet-500 to-indigo-400';
      case 'harmony': return 'from-cyan-500 to-blue-400';
      case 'melody': return 'from-emerald-500 to-teal-400';
      default: return 'from-slate-500 to-slate-400';
    }
  };

  return (
    <div className="w-full bg-[#121A2B] border border-slate-800 rounded-2xl p-5 shadow-xl">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-5">
        <div>
          <div className="flex items-center gap-2">
            <Sliders className="w-5 h-5 text-cyan-400" />
            <h3 className="font-semibold text-white text-base">Multi-Track Instrument Stem Mixer</h3>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Genuinely independent tracks composed with distinct musical parts. Mute, solo, adjust levels, or regenerate any stem.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-[11px] text-slate-400 bg-slate-800/80 px-2.5 py-1 rounded-md border border-slate-700">
            4 Independent Stems
          </span>
        </div>
      </div>

      {regenError && (
        <div className="mb-4 p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-xs text-red-300">
          {regenError}
        </div>
      )}

      {/* Channel Strips Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {['drums', 'bass', 'harmony', 'melody'].map(stemName => {
          const stemInfo = stems.find(s => s.name === stemName);
          const isMuted = mutedStems[stemName] || (soloStem !== null && soloStem !== stemName);
          const isSolo = soloStem === stemName;
          const currentGain = stemGains[stemName] ?? 0.8;
          const isRegenerating = regeneratingStem === stemName;

          return (
            <div
              key={stemName}
              className={`bg-[#192438] border rounded-xl p-4 flex flex-col justify-between transition-all ${
                isMuted ? 'border-slate-800 opacity-60' : 'border-slate-700 shadow-lg'
              }`}
            >
              {/* Channel Header */}
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <div className={`w-3 h-3 rounded-full bg-gradient-to-tr ${getStemColor(stemName)}`} />
                    <span className="font-bold text-sm text-white capitalize">{stemName}</span>
                  </div>
                  <span className="text-[10px] text-slate-400 font-mono">
                    {stemInfo ? `${stemInfo.lufs.toFixed(1)} LUFS` : '-16.0 LUFS'}
                  </span>
                </div>

                {/* Mute and Solo Buttons */}
                <div className="grid grid-cols-2 gap-2 mb-4">
                  <button
                    onClick={() => toggleMute(stemName)}
                    className={`py-1.5 rounded-lg text-xs font-bold transition-all ${
                      mutedStems[stemName]
                        ? 'bg-red-500 text-white shadow-md shadow-red-500/30'
                        : 'bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700'
                    }`}
                  >
                    MUTE
                  </button>

                  <button
                    onClick={() => toggleSolo(stemName)}
                    className={`py-1.5 rounded-lg text-xs font-bold transition-all ${
                      isSolo
                        ? 'bg-amber-500 text-slate-900 shadow-md shadow-amber-500/30'
                        : 'bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700'
                    }`}
                  >
                    SOLO
                  </button>
                </div>

                {/* Level Fader */}
                <div className="mb-4">
                  <div className="flex justify-between text-[11px] text-slate-400 mb-1">
                    <span>Level</span>
                    <span className="font-mono text-cyan-300 font-medium">
                      {(currentGain * 100).toFixed(0)}%
                    </span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="1.2"
                    step="0.02"
                    value={currentGain}
                    onChange={e => handleGainChange(stemName, parseFloat(e.target.value))}
                    className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-cyan-400"
                  />
                </div>
              </div>

              {/* Bottom Actions: Download and Regenerate */}
              <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between gap-2">
                <a
                  href={`/audio/${job.job_id}/stems/${stemName}.wav`}
                  download={`${job.job_id}_stem_${stemName}.wav`}
                  className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-[11px] text-slate-200 border border-slate-700 transition-colors"
                  title={`Download ${stemName}.wav`}
                >
                  <Download className="w-3 h-3 text-cyan-400" />
                  <span>WAV</span>
                </a>

                <button
                  onClick={() => handleRegenerateStem(stemName)}
                  disabled={isRegenerating}
                  className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-violet-600/20 hover:bg-violet-600/30 text-[11px] text-violet-300 border border-violet-500/30 transition-colors disabled:opacity-50"
                  title={`Regenerate ${stemName} variation`}
                >
                  <RefreshCw className={`w-3 h-3 ${isRegenerating ? 'animate-spin text-cyan-400' : ''}`} />
                  <span>{isRegenerating ? 'Regenerating...' : 'Regenerate'}</span>
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
