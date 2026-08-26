import { apiClient } from './client';
import { BackendHealthResponse } from './types';

export interface HealthCheckResult {
  isOnline: boolean;
  status: string;
  latencyMs: number;
  checkedAt: string;
  error?: string;
}

/**
 * Pings backend GET /api/v1/health to verify service and inference gateway availability.
 */
export const checkBackendHealth = async (): Promise<HealthCheckResult> => {
  const startTime = performance.now();
  try {
    const response = await apiClient.get<BackendHealthResponse>('/health', {
      timeout: 5000,
    });
    const latencyMs = Math.round(performance.now() - startTime);

    return {
      isOnline: response.data.status === 'ok',
      status: response.data.status || 'ok',
      latencyMs,
      checkedAt: new Date().toISOString(),
    };
  } catch (err: any) {
    const latencyMs = Math.round(performance.now() - startTime);
    return {
      isOnline: false,
      status: 'offline',
      latencyMs,
      checkedAt: new Date().toISOString(),
      error: err?.message || 'Connection refused',
    };
  }
};
