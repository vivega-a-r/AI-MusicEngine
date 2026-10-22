import type { JobResponse, MusicJobRequest, MusicManifest } from '../types';

const API_BASE = '/api/v1';

export class ApiError extends Error {
  code: string;
  retryable: boolean;
  details?: any;

  constructor(code: string, message: string, retryable: boolean = false, details?: any) {
    super(message);
    this.name = 'ApiError';
    this.code = code;
    this.retryable = retryable;
    this.details = details;
  }
}

async function requestJson<T>(url: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers || {});
  if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }

  // Get active dev user from localStorage
  const localUserId = localStorage.getItem('incubrix_user_id') || 'creator_pro';
  headers.set('X-User-Id', localUserId);

  const res = await fetch(url, { ...options, headers });
  
  if (!res.ok) {
    let errCode = `HTTP_${res.status}`;
    let errMsg = `Request failed with status ${res.status}`;
    let retryable = false;
    let details = undefined;

    try {
      const errBody = await res.json();
      if (errBody.error) {
        errCode = errBody.error.code || errCode;
        errMsg = errBody.error.message || errMsg;
        retryable = !!errBody.error.retryable;
        details = errBody.error.details;
      } else if (errBody.detail) {
        errMsg = typeof errBody.detail === 'string' ? errBody.detail : JSON.stringify(errBody.detail);
      }
    } catch {
      // Body not JSON
    }

    throw new ApiError(errCode, errMsg, retryable, details);
  }

  return res.json() as Promise<T>;
}

export const apiService = {
  async createJob(payload: MusicJobRequest, idempotencyKey?: string): Promise<JobResponse> {
    const headers: Record<string, string> = {};
    if (idempotencyKey) {
      headers['Idempotency-Key'] = idempotencyKey;
    }
    return requestJson<JobResponse>(`${API_BASE}/music/jobs`, {
      method: 'POST',
      headers,
      body: JSON.stringify(payload),
    });
  },

  async getJob(jobId: string): Promise<JobResponse> {
    return requestJson<JobResponse>(`${API_BASE}/jobs/${jobId}`);
  },

  async getManifest(jobId: string): Promise<MusicManifest> {
    return requestJson<MusicManifest>(`${API_BASE}/jobs/${jobId}/manifest`);
  },

  async regenerateStem(jobId: string, stemName: string, seed?: number): Promise<JobResponse> {
    return requestJson<JobResponse>(`${API_BASE}/jobs/${jobId}/stems/${stemName}/regenerate`, {
      method: 'POST',
      body: JSON.stringify({ seed }),
    });
  },

  async listJobs(limit: number = 30): Promise<{ total: number; jobs: JobResponse[] }> {
    return requestJson<{ total: number; jobs: JobResponse[] }>(`${API_BASE}/jobs?limit=${limit}`);
  },

  async deleteJob(jobId: string): Promise<{ message: string }> {
    return requestJson<{ message: string }>(`${API_BASE}/jobs/${jobId}`, {
      method: 'DELETE',
    });
  },
};
