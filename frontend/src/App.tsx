import React, { useEffect, useState } from 'react';
import { Navbar } from './components/Navbar';
import { StudioWorkspace } from './features/music-generation/StudioWorkspace';
import { AudioPlayer } from './features/audio-player/AudioPlayer';
import { StemMixer } from './features/stems/StemMixer';
import { HistoryView } from './features/history/HistoryView';
import { SettingsView } from './features/settings/SettingsView';
import { GenerationProgressModal } from './components/GenerationProgressModal';
import { TechnicalManifestModal } from './components/TechnicalManifestModal';
import type { JobResponse, MusicJobRequest, MusicManifest } from './types';
import { apiService } from './services/api';
import { Sparkles, Music } from 'lucide-react';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'studio' | 'history' | 'manifest' | 'settings'>('studio');
  const [userId, setUserId] = useState<string>(() => {
    return localStorage.getItem('incubrix_user_id') || 'creator_pro';
  });

  const [activeJob, setActiveJob] = useState<JobResponse | null>(null);
  const [pendingJob, setPendingJob] = useState<JobResponse | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [historyJobs, setHistoryJobs] = useState<JobResponse[]>([]);
  const [manifestModalOpen, setManifestModalOpen] = useState(false);
  const [selectedManifest, setSelectedManifest] = useState<MusicManifest | null>(null);

  // Sync user ID to localStorage
  const handleUpdateUserId = (newId: string) => {
    setUserId(newId);
    localStorage.setItem('incubrix_user_id', newId);
  };

  // Load history on mount
  const loadHistory = async () => {
    try {
      const res = await apiService.listJobs(30);
      setHistoryJobs(res.jobs);
      // If no active job yet, select the latest succeeded job if available
      if (!activeJob && res.jobs.length > 0) {
        const latestSucceeded = res.jobs.find(j => j.status === 'succeeded');
        if (latestSucceeded) {
          setActiveJob(latestSucceeded);
        }
      }
    } catch (e) {
      console.error("Failed to load jobs history:", e);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  // Handle music generation request
  const handleGenerate = async (request: MusicJobRequest) => {
    setIsGenerating(true);
    try {
      const job = await apiService.createJob(request);
      setPendingJob(job);

      // Poll until completed
      const pollInterval = setInterval(async () => {
        try {
          const updated = await apiService.getJob(job.job_id);
          setPendingJob(updated);

          if (updated.status === 'succeeded') {
            clearInterval(pollInterval);
            setIsGenerating(false);
            setPendingJob(null);
            setActiveJob(updated);
            loadHistory();
          } else if (updated.status === 'failed') {
            clearInterval(pollInterval);
            setIsGenerating(false);
            loadHistory();
          }
        } catch (pollErr) {
          console.error("Polling error:", pollErr);
        }
      }, 500);
    } catch (err: any) {
      console.error("Job creation failed:", err);
      setIsGenerating(false);
      setPendingJob(null);
      alert(err.message || "Failed to start music generation.");
    }
  };

  const handleDeleteJob = async (jobId: string) => {
    try {
      await apiService.deleteJob(jobId);
      if (activeJob?.job_id === jobId) {
        setActiveJob(null);
      }
      loadHistory();
    } catch (err) {
      console.error("Delete failed:", err);
    }
  };

  return (
    <div className="min-h-screen bg-[#0B1020] text-slate-100 flex flex-col font-sans selection:bg-cyan-500/30 selection:text-cyan-200">
      {/* Top Navbar */}
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} userId={userId} />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Studio View */}
        {activeTab === 'studio' && (
          <div className="space-y-8">
            {/* Hero Banner */}
            <div className="relative rounded-3xl overflow-hidden p-6 sm:p-10 border border-slate-800 bg-gradient-to-br from-[#121A2B] via-[#0E1526] to-[#0B1020] shadow-2xl">
              <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-br from-violet-600/20 via-cyan-500/15 to-transparent rounded-full blur-3xl pointer-events-none" />
              
              <div className="max-w-3xl space-y-3 relative z-10">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-violet-500/10 border border-violet-500/30 text-xs font-semibold text-cyan-300">
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>Real 48 kHz AI Procedural Music Synthesis</span>
                </div>
                <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-white leading-tight">
                  Original Background Music for Video
                </h1>
                <p className="text-sm sm:text-base text-slate-400 leading-relaxed max-w-2xl">
                  Transform natural-language prompts and video duration into 48 kHz instrumental soundtracks with genuine independent instrument stems and voiceover ducking.
                </p>
              </div>
            </div>

            {/* Studio Workspace Form */}
            <StudioWorkspace onGenerate={handleGenerate} isGenerating={isGenerating} />

            {/* Active Output Player & Stem Mixer */}
            {activeJob && activeJob.status === 'succeeded' && (
              <div className="space-y-6 pt-4 border-t border-slate-800/80">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-bold text-white flex items-center gap-2">
                    <Music className="w-5 h-5 text-cyan-400" />
                    <span>Active Production Project: #{activeJob.job_id.substring(4, 10)}</span>
                  </h2>
                  <span className="text-xs text-slate-400 font-mono">
                    LUFS: {activeJob.manifest?.master_measurements.integrated_lufs} • Peak: {activeJob.manifest?.master_measurements.true_peak_dbtp} dBTP
                  </span>
                </div>

                {/* Master Audio Player */}
                <AudioPlayer
                  job={activeJob}
                  onOpenManifest={() => {
                    setSelectedManifest(activeJob.manifest || null);
                    setManifestModalOpen(true);
                  }}
                />

                {/* Stem Mixer */}
                <StemMixer
                  job={activeJob}
                  onJobUpdated={(updated) => setActiveJob(updated)}
                />
              </div>
            )}
          </div>
        )}

        {/* History View */}
        {activeTab === 'history' && (
          <HistoryView
            jobs={historyJobs}
            onSelectJob={(job) => {
              setActiveJob(job);
              setActiveTab('studio');
            }}
            onDeleteJob={handleDeleteJob}
          />
        )}

        {/* Manifest Inspector View */}
        {activeTab === 'manifest' && (
          <div className="max-w-4xl mx-auto space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold text-white">Technical Audio Manifest</h2>
                <p className="text-xs text-slate-400 mt-1">
                  Inspect measurements, loudness compliance, and music-theoretic parameters of the active composition.
                </p>
              </div>
            </div>

            {activeJob?.manifest ? (
              <div className="bg-[#121A2B] border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-2xl space-y-6">
                <div className="flex items-center justify-between pb-4 border-b border-slate-800">
                  <span className="font-mono text-xs text-cyan-400 font-bold">
                    Job ID: {activeJob.manifest.job_id}
                  </span>
                  <a
                    href={`/api/v1/jobs/${activeJob.job_id}/manifest`}
                    download={`${activeJob.job_id}_manifest.json`}
                    className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 border border-slate-700"
                  >
                    Download JSON
                  </a>
                </div>

                {/* Pretty formatted JSON display */}
                <pre className="bg-[#0B1020] p-4 rounded-2xl border border-slate-800 text-xs font-mono text-slate-300 overflow-x-auto max-h-[600px]">
                  {JSON.stringify(activeJob.manifest, null, 2)}
                </pre>
              </div>
            ) : (
              <div className="bg-[#121A2B] border border-slate-800 rounded-3xl p-12 text-center text-slate-400">
                No active project manifest loaded. Generate music or select a job in History.
              </div>
            )}
          </div>
        )}

        {/* Settings View */}
        {activeTab === 'settings' && (
          <SettingsView userId={userId} onUpdateUserId={handleUpdateUserId} />
        )}
      </main>

      {/* Generation Progress Modal */}
      {isGenerating && <GenerationProgressModal job={pendingJob} />}

      {/* Technical Manifest Modal */}
      {manifestModalOpen && (
        <TechnicalManifestModal
          manifest={selectedManifest}
          onClose={() => setManifestModalOpen(false)}
        />
      )}

      {/* Footer */}
      <footer className="w-full border-t border-slate-800/80 bg-[#0B1020] py-6 text-center text-xs text-slate-500">
        <p>IncuBrix Music Studio • Procedural AI Background Music Engine for Video • 100% Royalty-Free & Commercial-Safe</p>
      </footer>
    </div>
  );
};

export default App;
