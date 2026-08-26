import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { ApiError } from './types';

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
export const API_V1_URL = `${API_BASE_URL}/api/v1`;

// Create Axios Instance
export const apiClient = axios.create({
  baseURL: API_V1_URL,
  timeout: 30000, // 30s timeout for model inference
  headers: {
    'Accept': 'application/json',
  },
});

// Request interceptor to inject X-Request-ID and track start time
apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const reqId = `vox-${Date.now().toString(36)}-${Math.random().toString(36).substring(2, 8)}`;
  if (!config.headers['X-Request-ID']) {
    config.headers['X-Request-ID'] = reqId;
  }
  // Store request start timestamp on config for latency measurement
  (config as any)._requestStartTime = performance.now();
  return config;
});

// Response interceptor to calculate latency and process headers
apiClient.interceptors.response.use(
  (response) => {
    const startTime = (response.config as any)?._requestStartTime;
    const latency = startTime ? Math.round(performance.now() - startTime) : 0;
    (response as any).latencyMs = latency;
    return response;
  },
  (error: AxiosError) => {
    return Promise.reject(normalizeApiError(error));
  }
);

/**
 * Normalizes Axios errors into typed ApiError objects
 */
export const normalizeApiError = (error: any): ApiError => {
  if (axios.isAxiosError(error)) {
    const status = error.response?.status;
    const data = error.response?.data as any;
    const requestId = (error.config?.headers?.['X-Request-ID'] as string) || (error.response?.headers?.['x-request-id'] as string);
    const retryAfterHeader = error.response?.headers?.['retry-after'];
    const retryAfterSeconds = retryAfterHeader ? parseInt(retryAfterHeader, 10) : undefined;

    let message = 'An unexpected server error occurred.';
    let detail: string | undefined = undefined;

    if (data && typeof data === 'object') {
      if (typeof data.detail === 'string') {
        detail = data.detail;
        message = data.detail;
      } else if (Array.isArray(data.detail)) {
        // Pydantic validation error array
        detail = data.detail.map((d: any) => `${d.loc?.join('.') || 'param'}: ${d.msg}`).join(', ');
        message = 'Invalid request parameters.';
      } else if (typeof data.message === 'string') {
        message = data.message;
      }
    }

    if (status === 400) {
      message = detail || 'Invalid audio payload or unsupported format.';
    } else if (status === 413) {
      message = 'Payload exceeds maximum limit of 15MB. Please upload a smaller audio sample.';
    } else if (status === 429) {
      message = retryAfterSeconds 
        ? `Rate limit exceeded. Please wait ${retryAfterSeconds} seconds before re-trying.`
        : 'Rate limit exceeded. Please slow down your requests.';
    } else if (status === 500) {
      message = detail || 'Internal server error during audio DSP or anti-spoofing model inference.';
    } else if (error.code === 'ERR_NETWORK' || !status) {
      return {
        isNetworkError: true,
        message: 'Unable to connect to VoxShield FastAPI backend (http://localhost:8000). Ensure the backend service is running.',
        requestId,
      };
    }

    return {
      statusCode: status,
      message,
      detail,
      requestId,
      retryAfterSeconds,
      isNetworkError: false,
    };
  }

  return {
    message: error?.message || 'An unknown error occurred.',
    isNetworkError: false,
  };
};
