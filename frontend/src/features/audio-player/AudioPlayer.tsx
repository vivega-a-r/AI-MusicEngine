import { useEffect, useRef, useState } from 'react';
import { Play, Pause, RotateCcw, Volume2, VolumeX, Download, Repeat } from 'lucide-react';
import type { JobResponse } from '../../types';

interface AudioPlayerProps {
  job: JobResponse;
  onOpenManifest?: () => void;
}

export const AudioPlayer: React.FC<AudioPlayerProps> = ({ job, onOpenManifest }) => {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(job.request.duration_s || 10);
  const [volume, setVolume] = useState(0.85);
  const [isMuted, setIsMuted] = useState(false);
  const [isLooping, setIsLooping] = useState(job.request.loopable || false);
  const [downloadOpen, setDownloadOpen] = useState(false);

  const audioSrc = job.result_urls?.mix_wav || `/audio/${job.job_id}/mix.wav`;

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const handleTimeUpdate = () => setCurrentTime(audio.currentTime);
    const handleLoadedMetadata = () => {
      if (audio.duration && !isNaN(audio.duration)) {
        setDuration(audio.duration);
      }
    };
    const handleEnded = () => {
      if (!isLooping) setIsPlaying(false);
    };

    audio.addEventListener('timeupdate', handleTimeUpdate);
    audio.addEventListener('loadedmetadata', handleLoadedMetadata);
    audio.addEventListener('ended', handleEnded);

    return () => {
      audio.removeEventListener('timeupdate', handleTimeUpdate);
      audio.removeEventListener('loadedmetadata', handleLoadedMetadata);
      audio.removeEventListener('ended', handleEnded);
    };
  }, [isLooping, audioSrc]);

  // Waveform visualization drawing
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animId: number;
    const width = canvas.width;
    const height = canvas.height;
    const barCount = 70;
    const barWidth = width / barCount - 2;

    const render = () => {
      ctx.clearRect(0, 0, width, height);

      const progress = duration > 0 ? currentTime / duration : 0;
      const currentBarIdx = Math.floor(progress * barCount);

      for (let i = 0; i < barCount; i++) {
        // Pseudo-random deterministic waveform profile based on index and seed
        const seedVal = (job.request.seed || 42) + i;
        const normalizedHeight = 0.2 + 0.7 * Math.abs(Math.sin(i * 0.25 + seedVal * 0.05));
        const barHeight = Math.max(6, normalizedHeight * (height - 8));
        const x = i * (barWidth + 2);
        const y = (height - barHeight) / 2;

        if (i <= currentBarIdx) {
          // Played bars: vibrant cyan to violet gradient
          const grad = ctx.createLinearGradient(0, y, 0, y + barHeight);
          grad.addColorStop(0, '#22D3EE');
          grad.addColorStop(1, '#8B5CF6');
          ctx.fillStyle = grad;
        } else {
          // Unplayed bars: muted slate
          ctx.fillStyle = '#334155';
        }

        ctx.beginPath();
        ctx.roundRect(x, y, barWidth, barHeight, 3);
        ctx.fill();
      }

      if (isPlaying) {
        animId = requestAnimationFrame(render);
      }
    };

    render();
    return () => cancelAnimationFrame(animId);
  }, [currentTime, duration, isPlaying, job.request.seed]);

  const togglePlay = () => {
    const audio = audioRef.current;
    if (!audio) return;
    if (isPlaying) {
      audio.pause();
      setIsPlaying(false);
    } else {
      audio.play().then(() => setIsPlaying(true)).catch((e: unknown) => console.error("Playback error:", e));
    }
  };

  const handleSeek = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    const audio = audioRef.current;
    if (!canvas || !audio || duration <= 0) return;

    const rect = canvas.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const ratio = Math.max(0, Math.min(1, clickX / rect.width));
    const newTime = ratio * duration;
    audio.currentTime = newTime;
    setCurrentTime(newTime);
  };

  const toggleMute = () => {
    const audio = audioRef.current;
    if (!audio) return;
    audio.muted = !isMuted;
    setIsMuted(!isMuted);
  };

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = parseFloat(e.target.value);
    setVolume(val);
    if (audioRef.current) {
      audioRef.current.volume = val;
      audioRef.current.muted = false;
      setIsMuted(false);
    }
  };

  const formatTime = (secs: number) => {
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60);
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  return (
    <div className="w-full bg-[#121A2B] border border-slate-800 rounded-2xl p-5 shadow-2xl relative overflow-hidden">
      {/* Background ambient glow */}
      <div className="absolute top-0 right-0 w-80 h-80 bg-violet-600/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-0 left-0 w-80 h-80 bg-cyan-600/10 rounded-full blur-3xl pointer-events-none" />

      {/* Hidden audio element */}
      <audio
        ref={audioRef}
        src={audioSrc}
        loop={isLooping}
        preload="metadata"
      />

      {/* Header Info */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="font-semibold text-white text-base truncate max-w-md">
              {job.request.prompt}
            </h3>
            <span className="text-xs px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
              48 kHz
            </span>
            <span className="text-xs px-2 py-0.5 rounded bg-violet-500/10 text-violet-300 border border-violet-500/30">
              {job.manifest?.bpm || job.request.tempo_bpm || 100} BPM
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Key: <span className="text-slate-200 font-medium">{job.manifest?.key || job.request.key || 'C major'}</span> • Target LUFS: <span className="text-slate-200 font-medium">{job.manifest?.master_measurements.integrated_lufs ?? -16.0}</span> • Peak: <span className="text-slate-200 font-medium">{job.manifest?.master_measurements.true_peak_dbtp ?? -1.0} dBTP</span>
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2">
          {onOpenManifest && (
            <button
              onClick={onOpenManifest}
              className="text-xs px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors"
            >
              Technical Manifest
            </button>
          )}

          {/* Download Dropdown */}
          <div className="relative">
            <button
              onClick={() => setDownloadOpen(!downloadOpen)}
              className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg bg-gradient-to-r from-violet-600 to-cyan-500 hover:from-violet-500 hover:to-cyan-400 text-white font-medium shadow-md shadow-violet-500/20 transition-all"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Download</span>
            </button>

            {downloadOpen && (
              <div className="absolute right-0 mt-2 w-52 bg-[#192438] border border-slate-700 rounded-xl shadow-2xl p-2 z-50">
                <a
                  href={`/api/v1/jobs/${job.job_id}/download`}
                  download
                  className="flex items-center gap-2 px-3 py-2 text-xs text-slate-200 hover:bg-slate-800 rounded-lg transition-colors"
                >
                  <span className="w-2 h-2 rounded-full bg-cyan-400" />
                  <span>Master Mix (WAV 48kHz)</span>
                </a>
                {job.result_urls?.mix_ducked_wav && (
                  <a
                    href={job.result_urls.mix_ducked_wav}
                    download
                    className="flex items-center gap-2 px-3 py-2 text-xs text-slate-200 hover:bg-slate-800 rounded-lg transition-colors"
                  >
                    <span className="w-2 h-2 rounded-full bg-emerald-400" />
                    <span>Ducked Mix (WAV)</span>
                  </a>
                )}
                <a
                  href={`/audio/${job.job_id}/midi/midi.zip`}
                  download
                  className="flex items-center gap-2 px-3 py-2 text-xs text-slate-200 hover:bg-slate-800 rounded-lg transition-colors"
                >
                  <span className="w-2 h-2 rounded-full bg-violet-400" />
                  <span>MIDI Tracks (ZIP)</span>
                </a>
                <a
                  href={`/api/v1/jobs/${job.job_id}/manifest`}
                  download
                  className="flex items-center gap-2 px-3 py-2 text-xs text-slate-200 hover:bg-slate-800 rounded-lg transition-colors"
                >
                  <span className="w-2 h-2 rounded-full bg-amber-400" />
                  <span>Manifest (JSON)</span>
                </a>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Interactive Waveform Canvas */}
      <div className="w-full bg-[#0B1020] rounded-xl p-3 border border-slate-800 mb-4 cursor-pointer">
        <canvas
          ref={canvasRef}
          width={700}
          height={80}
          onClick={handleSeek}
          className="w-full h-20 block"
        />
      </div>

      {/* Playback Controls & Scrubber */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        {/* Play/Pause & Time */}
        <div className="flex items-center gap-4">
          <button
            onClick={togglePlay}
            className="w-12 h-12 rounded-xl bg-gradient-to-tr from-violet-600 to-cyan-500 hover:scale-105 active:scale-95 transition-all flex items-center justify-center text-white shadow-lg shadow-violet-500/25"
          >
            {isPlaying ? <Pause className="w-5 h-5 fill-white" /> : <Play className="w-5 h-5 fill-white translate-x-0.5" />}
          </button>

          <button
            onClick={() => {
              if (audioRef.current) {
                audioRef.current.currentTime = 0;
                setCurrentTime(0);
              }
            }}
            title="Restart"
            className="w-8 h-8 rounded-lg bg-slate-800 hover:bg-slate-700 flex items-center justify-center text-slate-300 transition-colors"
          >
            <RotateCcw className="w-4 h-4" />
          </button>

          <button
            onClick={() => setIsLooping(!isLooping)}
            title={isLooping ? 'Looping enabled' : 'Enable loop'}
            className={`w-8 h-8 rounded-lg flex items-center justify-center transition-colors ${
              isLooping ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40' : 'bg-slate-800 hover:bg-slate-700 text-slate-400'
            }`}
          >
            <Repeat className="w-4 h-4" />
          </button>

          {/* Time indicator */}
          <div className="text-xs font-mono text-slate-300">
            <span className="text-cyan-400 font-semibold">{formatTime(currentTime)}</span>
            <span className="text-slate-500"> / </span>
            <span>{formatTime(duration)}</span>
          </div>
        </div>

        {/* Volume Slider */}
        <div className="flex items-center gap-2">
          <button onClick={toggleMute} className="text-slate-400 hover:text-slate-200">
            {isMuted || volume === 0 ? <VolumeX className="w-4 h-4 text-red-400" /> : <Volume2 className="w-4 h-4" />}
          </button>
          <input
            type="range"
            min="0"
            max="1"
            step="0.01"
            value={isMuted ? 0 : volume}
            onChange={handleVolumeChange}
            className="w-24 h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-cyan-400"
          />
        </div>
      </div>
    </div>
  );
};
