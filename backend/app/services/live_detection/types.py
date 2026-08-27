"""
Phase 5 Live Detection Engine — Data Types & Schemas.
"""

import time
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


class TemporalStabilityState(str, Enum):
    STABLE_SPOOF = "STABLE_SPOOF"
    STABLE_GENUINE = "STABLE_GENUINE"
    TRANSIENT_ANOMALY = "TRANSIENT_ANOMALY"
    CONFLICTING_TIMELINE = "CONFLICTING_TIMELINE"
    INSUFFICIENT_TIMELINE = "INSUFFICIENT_TIMELINE"


class DetectorAgreementState(str, Enum):
    HIGH_AGREEMENT = "HIGH_AGREEMENT"
    MODERATE_AGREEMENT = "MODERATE_AGREEMENT"
    DETECTOR_DISAGREEMENT = "DETECTOR_DISAGREEMENT"
    CONFLICTING_SIGNALS = "CONFLICTING_SIGNALS"


class LiveConfidenceState(str, Enum):
    SUPPORTED = "SUPPORTED"
    CONFLICTED = "CONFLICTED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


@dataclass
class LiveWindow:
    window_index: int
    start_time_seconds: float
    end_time_seconds: float
    synthetic_score: float
    replay_score: float
    risk_score: float
    confidence: float
    decision: str
    dominant_signal: str


@dataclass
class DetectorContributions:
    neural_score: float
    replay_score: float
    spectral_score: float
    temporal_score: float
    integrity_score: float
    generalization_score: float


@dataclass
class TemporalStabilityResult:
    stability_state: str
    variance_score: float
    consecutive_agreements: int
    window_count: int
    explanation: str


@dataclass
class DetectorAgreementResult:
    agreement_state: str
    agreed_detectors: List[str]
    disagreeing_detectors: List[str]
    dominant_evidence_type: str
    explanation: str


@dataclass
class LiveAnalysisResult:
    status: str                         # LIVE_ANALYSIS_COMPLETED
    decision: str                       # LIKELY_SPOOF, LIKELY_GENUINE, UNCERTAIN
    risk_level: str                     # LOW, MEDIUM, HIGH, CRITICAL
    risk_score: float                   # [0.0 - 100.0]
    confidence_state: str               # SUPPORTED, CONFLICTED, INSUFFICIENT_EVIDENCE
    confidence_score: float             # [0.0 - 1.0]
    detectors: Dict[str, Any]
    agreement: Dict[str, Any]
    temporal_stability: Dict[str, Any]
    windows: List[Dict[str, Any]]
    evidence: List[Dict[str, Any]]
    counter_evidence: List[Dict[str, Any]]
    recommendation: str
    processing_metadata: Dict[str, Any]
    validation_metadata: Dict[str, Any]
    limitations: List[str]


@dataclass
class LiveSessionState:
    session_id: str
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    chunks_received: int = 0
    accumulated_samples: int = 0
    sample_rate: int = 16000
    is_finalized: bool = False
    latest_assessment: Optional[Dict[str, Any]] = None
