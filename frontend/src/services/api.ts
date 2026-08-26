import { checkBackendHealth } from '../api/healthApi';
import { postAudioForAnalysis } from '../api/analysisApi';
import { BackendAnalysisResponse } from '../api/types';

export const checkHealth = async (): Promise<{ status: string }> => {
  const result = await checkBackendHealth();
  return { status: result.status };
};

export const analyzeAudio = async (
  audioFile: File | Blob
): Promise<BackendAnalysisResponse> => {
  const result = await postAudioForAnalysis(audioFile);
  return result.data;
};
