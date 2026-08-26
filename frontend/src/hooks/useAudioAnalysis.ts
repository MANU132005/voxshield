import { useState, useCallback } from 'react';
import { postAudioForAnalysis } from '../api/analysisApi';
import { enrichAnalysisResponse } from '../utils/forensicUtils';
import {
  EnrichedAnalysisResult,
  SessionAuditRecord,
  ApiError,
} from '../api/types';

export const useAudioAnalysis = () => {
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [activeResult, setActiveResult] = useState<EnrichedAnalysisResult | null>(null);
  const [error, setError] = useState<ApiError | string | null>(null);
  const [sessionRecords, setSessionRecords] = useState<SessionAuditRecord[]>([]);

  const runAnalysis = useCallback(
    async (
      audioFileOrBlob: File | Blob,
      metadata: {
        name: string;
        sizeBytes: number;
        mimeType?: string;
        durationSeconds?: number;
        source: 'MICROPHONE' | 'FILE_UPLOAD';
      }
    ) => {
      setIsAnalyzing(true);
      setError(null);

      try {
        const { data: rawResponse, latencyMs, requestId } = await postAudioForAnalysis(
          audioFileOrBlob,
          metadata.name
        );

        const enriched = enrichAnalysisResponse(
          rawResponse,
          {
            name: metadata.name,
            sizeBytes: metadata.sizeBytes,
            mimeType: metadata.mimeType || 'audio/wav',
            durationSeconds: metadata.durationSeconds,
            source: metadata.source,
          },
          latencyMs,
          requestId
        );

        setActiveResult(enriched);

        // Add to session investigation records
        const newRecord: SessionAuditRecord = {
          id: `audit-${Date.now()}-${Math.random().toString(36).substring(2, 6)}`,
          requestId,
          filename: metadata.name,
          fileSizeBytes: metadata.sizeBytes,
          durationSeconds: metadata.durationSeconds,
          timestamp: enriched.clientTimestamp,
          decision: enriched.decision,
          riskScore: enriched.raw.risk_score,
          riskStatus: enriched.raw.status,
          syntheticScore: enriched.raw.synthetic_score,
          replayScore: enriched.raw.replay_score,
          latencyMs,
          enrichedResult: enriched,
        };

        setSessionRecords((prev) => [newRecord, ...prev]);
      } catch (err: any) {
        console.error('Audio security analysis error:', err);
        setError(err);
      } finally {
        setIsAnalyzing(false);
      }
    },
    []
  );

  const selectRecord = useCallback((record: SessionAuditRecord) => {
    setActiveResult(record.enrichedResult);
    setError(null);
  }, []);

  const resetAnalysis = useCallback(() => {
    setActiveResult(null);
    setError(null);
  }, []);

  const clearSession = useCallback(() => {
    setSessionRecords([]);
  }, []);

  return {
    isAnalyzing,
    activeResult,
    error,
    sessionRecords,
    runAnalysis,
    selectRecord,
    resetAnalysis,
    clearSession,
  };
};
