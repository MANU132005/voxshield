/**
 * VoxShield Type Definitions
 * 
 * Strict typing reflecting both backend API contracts and frontend SOC data models.
 * Preserves scientific honesty: hypotheses are typed as hypotheses, scores preserve raw ranges.
 */

export type BackendRiskStatus = 'SAFE' | 'SUSPICIOUS' | 'HIGH_RISK';

/**
 * Exact schema returned by POST /api/v1/analyze
 */
export interface BackendAnalysisResponse {
  synthetic_score: number;
  replay_score: number;
  speaker_match: number | null;
  risk_score: number;
  status: BackendRiskStatus;
  reasons: string[];
}

/**
 * Health check response from GET /api/v1/health
 */
export interface BackendHealthResponse {
  status: string;
}

/**
 * Root service directory response from GET /
 */
export interface BackendRootResponse {
  message: string;
  docs: string;
  health: string;
}

/**
 * Security Console Decision Classification
 */
export type SecurityDecision = 'ALLOW' | 'STEP-UP' | 'BLOCK' | 'INCONCLUSIVE';

/**
 * Confidence Levels - Preserves ClaimGuard / scientific boundaries
 */
export type ConfidenceState = 
  | 'HIGH_MEASUREMENT_CONFIDENCE'
  | 'MODERATE'
  | 'LOW'
  | 'INSUFFICIENT_EVIDENCE';

/**
 * Evidence item directionality
 */
export type EvidenceDirection = 'SUPPORTS_SPOOF' | 'SUPPORTS_GENUINE' | 'INCONCLUSIVE';

export type EvidenceCategory = 'SYNTHETIC_AI' | 'REPLAY_DSP' | 'ACOUSTIC_QUALITY' | 'BIOMETRIC' | 'HEURISTIC';

export type EvidenceStrength = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO';

export interface ForensicEvidenceItem {
  id: string;
  category: EvidenceCategory;
  title: string;
  description: string;
  direction: EvidenceDirection;
  strength: EvidenceStrength;
  measuredValue?: string | number;
  claimStatus: 'CONFIRMED' | 'HEURISTIC' | 'OBSERVED';
}

/**
 * Attack Hypothesis - explicitly qualified as qualitative evaluation
 */
export interface AttackHypothesis {
  id: string;
  name: string;
  category: 
    | 'AI_SYNTHETIC_VOICE' 
    | 'VOICE_CONVERSION' 
    | 'NEURAL_TTS' 
    | 'PHYSICAL_REPLAY' 
    | 'TRANSDUCER_ARTIFACT' 
    | 'ENVIRONMENTAL_NOISE' 
    | 'AUTHENTIC_SPEECH';
  likelihood: 'VERY_HIGH' | 'HIGH' | 'MODERATE' | 'LOW' | 'UNLIKELY';
  description: string;
  indicators: string[];
  isHypothesisOnly: true;
}

/**
 * Forensic Processing Pipeline Stage
 */
export interface ForensicTimelineStage {
  stageNumber: number;
  name: string;
  subsystem: string;
  status: 'COMPLETED' | 'IN_PROGRESS' | 'PENDING' | 'SKIPPED';
  durationMs?: number;
  details?: string;
  benchmarkNotes?: string;
}

/**
 * Complete Enriched Analysis Audit Model
 */
export interface EnrichedAnalysisResult {
  requestId: string;
  clientTimestamp: string;
  audioMetadata: {
    name: string;
    sizeBytes: number;
    mimeType: string;
    durationSeconds?: number;
    source: 'MICROPHONE' | 'FILE_UPLOAD';
  };
  latencyMs: number;
  raw: BackendAnalysisResponse;
  decision: SecurityDecision;
  decisionReason: string;
  confidence: ConfidenceState;
  confidenceExplanation: string;
  evidenceList: ForensicEvidenceItem[];
  counterEvidenceList: ForensicEvidenceItem[];
  attackHypotheses: AttackHypothesis[];
  timeline: ForensicTimelineStage[];
  limitations: string[];
}

/**
 * Session Investigation Record for local SOC history
 */
export interface SessionAuditRecord {
  id: string;
  requestId: string;
  filename: string;
  fileSizeBytes: number;
  durationSeconds?: number;
  timestamp: string;
  decision: SecurityDecision;
  riskScore: number;
  riskStatus: BackendRiskStatus;
  syntheticScore: number;
  replayScore: number;
  latencyMs: number;
  enrichedResult: EnrichedAnalysisResult;
}

/**
 * Structured API Error Model
 */
export interface ApiError {
  statusCode?: number;
  message: string;
  detail?: string;
  requestId?: string;
  retryAfterSeconds?: number;
  isNetworkError?: boolean;
}
