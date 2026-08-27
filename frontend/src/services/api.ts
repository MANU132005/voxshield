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
  timeout: 30000,
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

  try {
    const formData = new FormData();
    const actualMime = audioFile.type || 'audio/webm';
    const ext = actualMime.includes('mp4') ? 'm4a' : actualMime.includes('webm') ? 'webm' : 'wav';

    const fileToUpload = audioFile instanceof File 
      ? audioFile 
      : new File([audioFile], `mic_recording.${ext}`, { type: actualMime });

    console.log(`[VOXSHIELD] Payload filename: ${fileToUpload.name}, MIME: ${fileToUpload.type}, Size: ${fileToUpload.size} bytes`);
    formData.append('file', fileToUpload);

    const response = await apiClient.post<AnalysisResult>('/analyze', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    console.log('[VOXSHIELD] Real Backend response received:', response.data);
    return { ...response.data, isDemo: false };
  } catch (error: any) {
    console.error('[VOXSHIELD] Real backend analysis failed:', error);
    const errorDetail = error.response?.data?.detail 
      || (error.code === 'ECONNABORTED' ? 'Backend request timed out (30s).' : null)
      || (error.response ? `HTTP ${error.response.status}: Analysis request failed.` : null)
      || 'Unable to connect to VoxShield backend at ' + targetUrl;

    throw new Error(`Real backend analysis failed. No simulated result was used. Details: ${errorDetail}`);
  }
};
