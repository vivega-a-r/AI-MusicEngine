export interface SectionItem {
  start_s: number;
  mood: string;
}

export interface OutputConfig {
  sample_rate: number;
  target_lufs: number;
  formats: string[];
}

export interface MusicJobRequest {
  prompt: string;
  duration_s: number;
  sections?: SectionItem[];
  tempo_bpm?: number;
  key?: string;
  loopable: boolean;
  seed?: number;
  narration_url?: string;
  output: OutputConfig;
}

export interface AudioMeasurements {
  sample_rate: number;
  bit_depth: number;
  channels: number;
  requested_duration_s: number;
  actual_duration_s: number;
  duration_difference_s: number;
  integrated_lufs: number;
  true_peak_dbtp: number;
  max_sample_peak: number;
  clipping_detected: boolean;
}

export interface StemInfo {
  name: string;
  file_path: string;
  download_url: string;
  gain: number;
  duration_s: number;
  duration_diff_s: number;
  sample_rate: number;
  lufs: number;
  true_peak_dbtp: number;
}

export interface DuckingDetails {
  applied: boolean;
  narration_detected_speech: boolean;
  speech_duration_s: number;
  ducking_reduction_db: number;
  attack_ms: number;
  release_ms: number;
  message: string;
}

export interface LoopValidation {
  loopable_requested: boolean;
  is_seamless: boolean;
  boundary_discontinuity: number;
  crossfade_duration_s: number;
  validation_status: string;
}

export interface MusicManifest {
  manifest_version: string;
  job_id: string;
  created_at: string;
  user_id: string;
  original_prompt: string;
  normalized_prompt: string;
  musical_parameters: {
    primary_mood?: string;
    genre?: string;
    energy?: number;
    instruments?: Record<string, string>;
    [key: string]: any;
  };
  bpm: number;
  meter: string;
  key: string;
  scale: string;
  seed: number;
  chord_progression: string[];
  section_timeline: Array<{ start_s: number; mood: string }>;
  master_measurements: AudioMeasurements;
  stems: StemInfo[];
  composition_method: string;
  rendering_engine: string;
  libraries_used: Record<string, string>;
  processing_time_s: number;
  cost_estimate_usd: number;
  cost_explanation: string;
  instrumental_output: boolean;
  ai_generation_label: string;
  license_info: {
    output_license: string;
    sound_source: string;
    commercial_safe: boolean;
  };
  narration_ducking?: DuckingDetails;
  loop_validation?: LoopValidation;
  warnings: string[];
  validation_passed: boolean;
}

export interface JobResultUrls {
  mix_wav?: string;
  mix_mp3?: string;
  mix_ducked_wav?: string;
  stems: Record<string, string>;
  midi_zip?: string;
  manifest_json?: string;
}

export interface JobResponse {
  job_id: string;
  status: 'queued' | 'running' | 'succeeded' | 'failed';
  progress: number;
  current_stage: string;
  created_at: string;
  updated_at: string;
  user_id: string;
  request: MusicJobRequest;
  result_urls?: JobResultUrls;
  manifest?: MusicManifest;
  error?: {
    code: string;
    message: string;
    retryable: boolean;
    details?: any;
  };
}

export interface UserProfile {
  user_id: string;
  email: string;
  auth_provider: 'local_dev_mode' | 'firebase';
}
