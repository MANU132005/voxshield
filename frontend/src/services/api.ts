import axios from 'axios';
import { AnalysisResult, RiskStatus } from '../types/analysis';
import { mockAnalyzeAudio } from './mockApi';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const DEFAULT_USE_MOCK = import.meta.env.VITE_USE_MOCK_API !== 'false';

const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Accept': 'application/json',
  },
});

export const checkHealth = async (): Promise<{ status: string }> => {
  try {
    const response = await apiClient.get('/health');
    return response.data;
  } catch (error) {
    return { status: 'offline' };
  }
};

export const analyzeAudio = async (
  audioFile: File | Blob,
  forceMock: boolean = DEFAULT_USE_MOCK,
  presetStatus?: RiskStatus
): Promise<AnalysisResult> => {
  if (forceMock) {
    return await mockAnalyzeAudio(audioFile, presetStatus);
  }

  try {
    const formData = new FormData();
    const fileToUpload = audioFile instanceof File 
      ? audioFile 
      : new File([audioFile], 'mic_recording.wav', { type: 'audio/wav' });

    formData.append('file', fileToUpload);

    const response = await apiClient.post<AnalysisResult>('/analyze', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  } catch (error) {
    console.warn('Real FastAPI backend unreachable. Falling back to Mock API response.', error);
    return await mockAnalyzeAudio(audioFile, presetStatus);
  }
};
