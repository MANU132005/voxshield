export type RiskStatus = 'SAFE' | 'SUSPICIOUS' | 'HIGH_RISK';

export interface AnalysisResult {
  synthetic_score: number;
  replay_score: number;
  speaker_match: number | null;
  risk_score: number;
  status: RiskStatus;
  reasons: string[];
}

export interface SamplePreset {
  id: string;
  name: string;
  type: 'SAFE' | 'SUSPICIOUS' | 'HIGH_RISK';
  description: string;
  duration: string;
}
