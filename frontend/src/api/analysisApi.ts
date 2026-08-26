import { apiClient } from './client';
import { BackendAnalysisResponse } from './types';

export interface AnalysisApiResult {
  data: BackendAnalysisResponse;
  latencyMs: number;
  requestId: string;
}

/**
 * Sends audio payload to POST /api/v1/analyze for neural anti-spoofing and DSP replay evaluation.
 */
export const postAudioForAnalysis = async (
  audioFileOrBlob: File | Blob,
  fileName?: string
): Promise<AnalysisApiResult> => {
  // Client-side pre-flight validations
  if (audioFileOrBlob.size === 0) {
    throw new Error('Audio sample is empty. Please record or upload an audio file containing voice data.');
  }

  const MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024; // 15MB backend limit
  if (audioFileOrBlob.size > MAX_FILE_SIZE_BYTES) {
    throw new Error('Audio sample exceeds 15MB limit. Please upload a smaller audio file.');
  }

  const resolvedName = audioFileOrBlob instanceof File 
    ? audioFileOrBlob.name 
    : (fileName || `mic_recording_${Date.now()}.wav`);

  const resolvedType = audioFileOrBlob.type || 'audio/wav';

  const filePayload = audioFileOrBlob instanceof File
    ? audioFileOrBlob
    : new File([audioFileOrBlob], resolvedName, { type: resolvedType });

  const formData = new FormData();
  formData.append('file', filePayload);

  const response = await apiClient.post<BackendAnalysisResponse>('/analyze', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  const latencyMs = (response as any).latencyMs || 0;
  const requestId = (response.config.headers?.['X-Request-ID'] as string) || 
                    (response.headers?.['x-request-id'] as string) || 
                    `req-${Date.now()}`;

  return {
    data: response.data,
    latencyMs,
    requestId,
  };
};
