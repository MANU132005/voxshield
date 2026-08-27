import { AnalysisResult, RiskStatus } from '../types/analysis';

const mockResponses: Record<RiskStatus, AnalysisResult> = {
  SAFE: {
    synthetic_score: 0.08,
    replay_score: 0.05,
    speaker_match: null,
    risk_score: 0.07,
    status: 'SAFE',
    isDemo: true,
    reasons: [
      'Natural phase dynamics and clean harmonic spectrum detected',
      'No synthetic audio artifacts present'
    ]
  },
  SUSPICIOUS: {
    synthetic_score: 0.52,
    replay_score: 0.48,
    speaker_match: null,
    risk_score: 0.50,
    status: 'SUSPICIOUS',
    isDemo: true,
    reasons: [
      'Elevated synthetic voice probability detected',
      'Minor acoustic reverberation anomalies present'
    ]
  },
  HIGH_RISK: {
    synthetic_score: 0.94,
    replay_score: 0.76,
    speaker_match: null,
    risk_score: 0.91,
    status: 'HIGH_RISK',
    isDemo: true,
    reasons: [
      'Synthetic voice characteristics detected',
      'Possible replay characteristics detected'
    ]
  }
};

/**
 * Simulated Audio Analysis API service for Frontend Mock Mode.
 * Allows Developer 2 to build and refine the UI completely independently.
 */
export const mockAnalyzeAudio = async (
  fileOrBlob: File | Blob,
  presetStatus?: RiskStatus
): Promise<AnalysisResult> => {
  // Simulate network latency (800ms - 1500ms)
  const delay = Math.floor(Math.random() * 700) + 800;
  await new Promise((resolve) => setTimeout(resolve, delay));

  if (presetStatus && mockResponses[presetStatus]) {
    return mockResponses[presetStatus];
  }

  // Randomly assign sample result if no preset specified
  const filename = fileOrBlob instanceof File ? fileOrBlob.name.toLowerCase() : 'recording.wav';
  if (filename.includes('clone') || filename.includes('fake') || filename.includes('ai')) {
    return mockResponses.HIGH_RISK;
  } else if (filename.includes('replay') || filename.includes('echo')) {
    return mockResponses.SUSPICIOUS;
  } else if (filename.includes('safe') || filename.includes('human')) {
    return mockResponses.SAFE;
  }

  // Default balanced result
  return mockResponses.HIGH_RISK;
};
