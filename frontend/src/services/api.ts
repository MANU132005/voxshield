import axios from 'axios';
import { AnalysisResult, RiskStatus } from '../types/analysis';
import { mockAnalyzeAudio } from './mockApi';

const rawBaseUrl = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').trim().replace(/\/+$/, '');
const API_BASE_URL = rawBaseUrl.endsWith('/api/v1') ? rawBaseUrl : `${rawBaseUrl}/api/v1`;
const DEFAULT_USE_MOCK = import.meta.env.VITE_USE_MOCK_API === 'true';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Accept': 'application/json',
  },
  timeout: 90000,
});

export const checkHealth = async (): Promise<{ status: string }> => {
  try {
    const response = await apiClient.get('/health');
    return response.data;
  } catch (error) {
    try {
      const rootUrl = rawBaseUrl.replace(/\/api\/v1$/, '');
      const rootClient = axios.create({ baseURL: rootUrl, timeout: 5000 });
      const response = await rootClient.get('/health');
      return response.data;
    } catch {
      return { status: 'offline' };
    }
  }
};

export const analyzeAudio = async (
  audioFile: File | Blob,
  forceMock: boolean = DEFAULT_USE_MOCK,
  presetStatus?: RiskStatus
): Promise<AnalysisResult> => {
  if (forceMock || presetStatus) {
    console.log('[VOXSHIELD] DEMO PRESET ANALYSIS SELECTED:', presetStatus || 'MOCK_MODE');
    const mockRes = await mockAnalyzeAudio(audioFile, presetStatus);
    return { ...mockRes, isDemo: true };
  }

  const targetUrl = `${API_BASE_URL}/analyze`;
  console.log('[VOXSHIELD] REAL API ANALYSIS - Sending POST request to:', targetUrl);

  const formData = new FormData();
  const actualMime = audioFile.type || 'audio/webm';
  const ext = actualMime.includes('mp4') ? 'm4a' : actualMime.includes('webm') ? 'webm' : 'wav';

  const fileToUpload = audioFile instanceof File 
    ? audioFile 
    : new File([audioFile], `mic_recording.${ext}`, { type: actualMime });

  formData.append('file', fileToUpload);

  const maxAttempts = 4;
  let lastError: any = null;

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      if (attempt > 1) {
        console.log(`[VOXSHIELD] Retry attempt ${attempt}/${maxAttempts} waking backend...`);
        await new Promise(res => setTimeout(res, 4000));
      }

      const response = await apiClient.post<AnalysisResult>('/analyze', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      console.log('[VOXSHIELD] Real Backend response received:', response.data);
      return { ...response.data, isDemo: false };
    } catch (error: any) {
      lastError = error;
      console.warn(`[VOXSHIELD] Real backend analysis attempt ${attempt} failed:`, error.message);

      // If it's a 400 Bad Request (e.g. silence or invalid format), do NOT retry, throw immediately
      if (error.response && error.response.status === 400) {
        break;
      }
    }
  }

  const errorDetail = lastError?.response?.data?.detail 
    || (lastError?.code === 'ECONNABORTED' ? 'Backend request timed out (90s). Render server was sleeping. Please try again.' : null)
    || (lastError?.response ? `HTTP ${lastError.response.status}: Analysis request failed.` : null)
    || 'Unable to connect to VoxShield backend at ' + targetUrl + ' (Server may be starting up).';

  throw new Error(`Real backend analysis failed. No simulated result was used. Details: ${errorDetail}`);
};
