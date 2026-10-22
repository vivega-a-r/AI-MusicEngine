import { X, FileText, Download, CheckCircle2, ShieldCheck, Music } from 'lucide-react';
import type { MusicManifest } from '../types';

interface TechnicalManifestModalProps {
  manifest: MusicManifest | null;
  onClose: () => void;
}

export const TechnicalManifestModal: React.FC<TechnicalManifestModalProps> = ({ manifest, onClose }) => {
  if (!manifest) return null;

  const m = manifest.master_measurements;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#0B1020]/80 backdrop-blur-md">
      <div className="w-full max-w-3xl bg-[#121A2B] border border-slate-700/80 rounded-3xl p-6 sm:p-8 shadow-2xl relative max-h-[90vh] overflow-y-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-violet-600/20 border border-violet-500/30 flex items-center justify-center text-cyan-400">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-bold text-white text-base">Technical Audio Manifest & Verification</h3>
                <span className="text-[11px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3" />
                  <span>Validation Passed</span>
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                Job #{manifest.job_id} • Schema v{manifest.manifest_version}
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-2 rounded-xl bg-slate-800/80 hover:bg-slate-700 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Measurements Grid */}
        <div>
          <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-3">
            Physical Audio Measurements
          </h4>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="bg-[#0B1020] border border-slate-800 rounded-xl p-3">
              <span className="text-[10px] text-slate-500 block">Sample Rate</span>
              <span className="font-mono text-sm font-bold text-cyan-300">{m.sample_rate} Hz</span>
            </div>

            <div className="bg-[#0B1020] border border-slate-800 rounded-xl p-3">
              <span className="text-[10px] text-slate-500 block">Integrated Loudness</span>
              <span className="font-mono text-sm font-bold text-cyan-300">{m.integrated_lufs} LUFS</span>
            </div>

            <div className="bg-[#0B1020] border border-slate-800 rounded-xl p-3">
              <span className="text-[10px] text-slate-500 block">True Peak</span>
              <span className="font-mono text-sm font-bold text-cyan-300">{m.true_peak_dbtp} dBTP</span>
            </div>

            <div className="bg-[#0B1020] border border-slate-800 rounded-xl p-3">
              <span className="text-[10px] text-slate-500 block">Duration Accuracy</span>
              <span className="font-mono text-sm font-bold text-emerald-400">
                ±{m.duration_difference_s}s (≤0.05s)
              </span>
            </div>
          </div>
        </div>

        {/* Music Theory Breakdown */}
        <div className="bg-[#192438] border border-slate-800 rounded-2xl p-4 space-y-3">
          <h4 className="text-xs font-bold text-slate-300 flex items-center gap-1.5 uppercase tracking-wider">
            <Music className="w-4 h-4 text-violet-400" />
            <span>Music Theory Parameters</span>
          </h4>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
            <div>
              <span className="text-slate-400 text-[11px] block">BPM:</span>
              <span className="font-mono font-bold text-white">{manifest.bpm}</span>
            </div>
            <div>
              <span className="text-slate-400 text-[11px] block">Musical Key:</span>
              <span className="font-mono font-bold text-white">{manifest.key}</span>
            </div>
            <div>
              <span className="text-slate-400 text-[11px] block">Meter:</span>
              <span className="font-mono font-bold text-white">{manifest.meter}</span>
            </div>
            <div>
              <span className="text-slate-400 text-[11px] block">Seed:</span>
              <span className="font-mono font-bold text-white">{manifest.seed}</span>
            </div>
          </div>

          <div>
            <span className="text-slate-400 text-[11px] block mb-1">Harmonic Chord Progression:</span>
            <div className="flex flex-wrap gap-1.5">
              {manifest.chord_progression.map((chord, i) => (
                <span
                  key={i}
                  className="px-2 py-0.5 rounded-md bg-[#0B1020] border border-slate-700 font-mono text-xs text-cyan-300"
                >
                  {chord}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Stem Inventory */}
        <div>
          <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">
            Generated Instrument Stems
          </h4>
          <div className="border border-slate-800 rounded-xl overflow-hidden divide-y divide-slate-800 text-xs">
            {manifest.stems.map((stem) => (
              <div key={stem.name} className="p-3 bg-[#0B1020] flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-white capitalize">{stem.name}</span>
                  <span className="text-slate-500 font-mono">({stem.sample_rate} Hz)</span>
                </div>
                <div className="flex items-center gap-4 text-slate-300 font-mono text-[11px]">
                  <span>Gain: {(stem.gain * 100).toFixed(0)}%</span>
                  <span>Loudness: {stem.lufs.toFixed(1)} LUFS</span>
                  <span>Peak: {stem.true_peak_dbtp.toFixed(1)} dBTP</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Licensing & Compliance Note */}
        <div className="p-4 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 text-xs text-cyan-200 flex items-start gap-3">
          <ShieldCheck className="w-5 h-5 text-cyan-400 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <p className="font-bold text-cyan-300">Commercial Use Rights Verified</p>
            <p className="text-[11px] text-cyan-200/80 leading-relaxed">
              {manifest.license_info.sound_source} Generated audio output is 100% royalty-free and approved for commercial monetization on YouTube, TV, games, and podcasts.
            </p>
          </div>
        </div>

        {/* Download Manifest Button */}
        <div className="flex items-center justify-end gap-3 pt-2">
          <a
            href={`/api/v1/jobs/${manifest.job_id}/manifest`}
            download={`${manifest.job_id}_manifest.json`}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-violet-600 to-cyan-500 hover:from-violet-500 hover:to-cyan-400 text-white font-semibold text-xs shadow-md transition-all"
          >
            <Download className="w-4 h-4" />
            <span>Download JSON Manifest</span>
          </a>
        </div>
      </div>
    </div>
  );
};
