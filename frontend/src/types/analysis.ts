export type RiskStatus = 'SAFE' | 'SUSPICIOUS' | 'HIGH_RISK';

export interface EvidenceItem {
  code?: string;
  category?: string;
  observed_value?: number;
  threshold?: number;
  message?: string;
}

export interface TimelineStage {
  stage_id: number;
  stage_name: string;
  execution_time_ms: number;
}

export interface AnalysisResult {
  synthetic_score: number;
  replay_score: number;
  speaker_match: number | null;
  risk_score: number;
  status: RiskStatus;
  reasons: string[];
  verdict?: string;
  risk_level?: string;
  evaluator_version?: string;
  evidence?: EvidenceItem[];
  forensic_timeline?: TimelineStage[];
  isDemo?: boolean;
}

export interface SamplePreset {
  id: string;
  name: string;
  type: 'SAFE' | 'SUSPICIOUS' | 'HIGH_RISK';
  description: string;
  duration: string;
}
