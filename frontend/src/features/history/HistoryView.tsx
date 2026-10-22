import { useState } from 'react';
import { History, Play, Trash2, Download, Search, CheckCircle2, Clock } from 'lucide-react';
import type { JobResponse } from '../../types';

interface HistoryViewProps {
  jobs: JobResponse[];
  onSelectJob: (job: JobResponse) => void;
  onDeleteJob: (jobId: string) => void;
}

export const HistoryView: React.FC<HistoryViewProps> = ({ jobs, onSelectJob, onDeleteJob }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null);

  const filtered = jobs.filter(j => 
    j.request.prompt.toLowerCase().includes(searchQuery.toLowerCase()) ||
    j.job_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (j.manifest?.key && j.manifest.key.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <div className="w-full max-w-5xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <History className="w-5 h-5 text-cyan-400" />
            <span>Generation History</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Access previous compositions, reload tracks into the mixer, and export audio stems.
          </p>
        </div>

        {/* Search */}
        <div className="relative w-full sm:w-64">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search by prompt or key..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-[#121A2B] border border-slate-700 rounded-xl pl-9 pr-4 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-400"
          />
        </div>
      </div>

      {filtered.length === 0 ? (
        <div className="bg-[#121A2B] border border-slate-800 rounded-3xl p-12 text-center space-y-3">
          <History className="w-10 h-10 text-slate-600 mx-auto" />
          <h3 className="text-sm font-semibold text-slate-300">No Generated Jobs Found</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto">
            Create your first background music composition in the Studio to see it listed here.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map((job) => (
            <div
              key={job.job_id}
              className="bg-[#121A2B] border border-slate-800 hover:border-slate-700/80 rounded-2xl p-4 sm:p-5 shadow-lg transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-4"
            >
              {/* Info */}
              <div className="flex-1 space-y-1.5">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="font-mono text-[11px] text-cyan-400 font-bold">
                    #{job.job_id.substring(4, 10)}
                  </span>
                  <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                    {job.request.duration_s}s
                  </span>
                  <span className="text-xs px-2 py-0.5 rounded bg-violet-500/10 text-violet-300 border border-violet-500/30">
                    {job.manifest?.bpm || job.request.tempo_bpm || 100} BPM
                  </span>
                  <span className="text-xs px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-300 border border-cyan-500/30">
                    {job.manifest?.key || job.request.key || 'C major'}
                  </span>
                  {job.status === 'succeeded' ? (
                    <span className="flex items-center gap-1 text-[11px] text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
                      <CheckCircle2 className="w-3 h-3" />
                      <span>Ready</span>
                    </span>
                  ) : (
                    <span className="flex items-center gap-1 text-[11px] text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded-full border border-amber-500/20">
                      <Clock className="w-3 h-3 animate-spin" />
                      <span>{job.status}</span>
                    </span>
                  )}
                </div>

                <p className="text-sm font-medium text-white line-clamp-1">
                  {job.request.prompt}
                </p>

                <p className="text-[11px] text-slate-500 font-mono">
                  {new Date(job.created_at).toLocaleString()} • Stems: 4 • LUFS: {job.manifest?.master_measurements.integrated_lufs ?? -16.0}
                </p>
              </div>

              {/* Actions */}
              <div className="flex items-center gap-2 shrink-0">
                <button
                  onClick={() => onSelectJob(job)}
                  className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-gradient-to-r from-violet-600 to-cyan-500 hover:from-violet-500 hover:to-cyan-400 text-xs font-semibold text-white shadow-md shadow-violet-500/20 transition-all"
                >
                  <Play className="w-3.5 h-3.5 fill-white" />
                  <span>Open & Mix</span>
                </button>

                <a
                  href={`/api/v1/jobs/${job.job_id}/download`}
                  download
                  className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors"
                  title="Download Master Mix"
                >
                  <Download className="w-4 h-4" />
                </a>

                {deleteConfirmId === job.job_id ? (
                  <div className="flex items-center gap-1 bg-red-900/30 p-1 rounded-xl border border-red-500/40">
                    <button
                      onClick={() => onDeleteJob(job.job_id)}
                      className="px-2 py-1 rounded-lg bg-red-600 text-[11px] font-bold text-white hover:bg-red-500"
                    >
                      Confirm
                    </button>
                    <button
                      onClick={() => setDeleteConfirmId(null)}
                      className="px-2 py-1 rounded-lg bg-slate-800 text-[11px] text-slate-300 hover:bg-slate-700"
                    >
                      Cancel
                    </button>
                  </div>
                ) : (
                  <button
                    onClick={() => setDeleteConfirmId(job.job_id)}
                    className="p-2 rounded-xl bg-slate-800 hover:bg-red-500/20 text-slate-400 hover:text-red-400 border border-slate-700 transition-colors"
                    title="Delete Job"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
