import { CheckCircle2, AlertCircle } from 'lucide-react';
import type { JobResponse } from '../types';

interface GenerationProgressModalProps {
  job: JobResponse | null;
  onCancel?: () => void;
}

export const GenerationProgressModal: React.FC<GenerationProgressModalProps> = ({ job }) => {
  if (!job) return null;

  const progress = job.progress || 0;
  const stage = job.current_stage || "Initializing composition engine...";
  const isFailed = job.status === 'failed';

  const stages = [
    { label: 'Prompt NLP & Musical Theory', threshold: 15 },
    { label: 'Stem Synthesis (Drums, Bass, Harmony, Melody)', threshold: 45 },
    { label: 'Stem Mixing & LUFS Mastering', threshold: 65 },
    { label: 'Loop Crossfade & Voiceover Ducking', threshold: 80 },
    { label: 'MIDI Export & Manifest Verification', threshold: 95 },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#0B1020]/80 backdrop-blur-md">
      <div className="w-full max-w-lg bg-[#121A2B] border border-slate-700/80 rounded-3xl p-6 sm:p-8 shadow-2xl relative overflow-hidden space-y-6">
        {/* Glow ambient */}
        <div className="absolute top-0 right-0 w-48 h-48 bg-violet-600/20 rounded-full blur-2xl pointer-events-none" />

        {/* Header with animated EQ */}
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-violet-600 to-cyan-500 p-[1px] flex items-center justify-center shadow-lg shadow-violet-500/25">
            <div className="w-full h-full bg-[#121A2B] rounded-2xl flex items-center justify-center gap-1">
              <span className="w-1 bg-cyan-400 rounded-full eq-bar-1" />
              <span className="w-1 bg-violet-400 rounded-full eq-bar-2" />
              <span className="w-1 bg-cyan-300 rounded-full eq-bar-3" />
              <span className="w-1 bg-violet-300 rounded-full eq-bar-4" />
              <span className="w-1 bg-cyan-400 rounded-full eq-bar-5" />
            </div>
          </div>

          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-lg font-bold text-white">Composing Original Music</h3>
              <span className="text-xs px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-300 border border-cyan-500/30">
                Job #{job.job_id.substring(4, 10)}
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Real-time procedural synthesis pipeline running locally
            </p>
          </div>
        </div>

        {/* Progress Bar & Percentage */}
        <div className="space-y-2">
          <div className="flex justify-between items-center text-xs">
            <span className="font-semibold text-cyan-300">{stage}</span>
            <span className="font-mono font-bold text-white">{progress}%</span>
          </div>

          <div className="w-full h-3 bg-[#0B1020] rounded-full overflow-hidden border border-slate-800 p-0.5">
            <div
              className="h-full bg-gradient-to-r from-violet-600 via-cyan-400 to-emerald-400 rounded-full transition-all duration-300"
              style={{ width: `${Math.max(5, progress)}%` }}
            />
          </div>
        </div>

        {/* Stages Checklist */}
        <div className="space-y-2 pt-2 border-t border-slate-800">
          {stages.map((stg, idx) => {
            const isCompleted = progress >= stg.threshold;
            const isCurrent = progress < stg.threshold && (idx === 0 || progress >= stages[idx - 1].threshold);

            return (
              <div
                key={idx}
                className={`flex items-center gap-3 text-xs transition-colors ${
                  isCompleted ? 'text-slate-300 font-medium' : (isCurrent ? 'text-cyan-400 font-bold' : 'text-slate-600')
                }`}
              >
                {isCompleted ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                ) : isCurrent ? (
                  <div className="w-4 h-4 rounded-full border-2 border-cyan-400 border-t-transparent animate-spin shrink-0" />
                ) : (
                  <div className="w-4 h-4 rounded-full border border-slate-700 shrink-0" />
                )}
                <span>{stg.label}</span>
              </div>
            );
          })}
        </div>

        {isFailed && (
          <div className="p-4 rounded-2xl bg-red-500/10 border border-red-500/30 text-xs text-red-300 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-400 shrink-0" />
            <div>
              <p className="font-bold">Generation Failed</p>
              <p className="mt-1">{job.error?.message || "An unexpected error occurred during audio synthesis."}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
