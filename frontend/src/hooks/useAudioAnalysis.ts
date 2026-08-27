import { useState } from 'react';
import { AnalysisResult, RiskStatus } from '../types/analysis';
import { analyzeAudio } from '../services/api';

export const useAudioAnalysis = () => {
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isMockMode, setIsMockMode] = useState<boolean>(false);

  const runAnalysis = async (
    fileOrBlob: File | Blob, 
    presetStatus?: RiskStatus
  ) => {
    setIsAnalyzing(true);
    setError(null);
    try {
      const data = await analyzeAudio(fileOrBlob, isMockMode, presetStatus);
      setResult(data);
    } catch (err: any) {
      setError(err?.message || 'Failed to analyze audio sample.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const resetAnalysis = () => {
    setResult(null);
    setError(null);
  };

  return {
    isAnalyzing,
    result,
    error,
    isMockMode,
    setIsMockMode,
    runAnalysis,
    resetAnalysis,
  };
};
