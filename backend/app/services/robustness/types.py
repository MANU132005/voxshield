"""
Phase 4 Real-World Security & Robustness Validation — Data Types & Models.
"""

import time
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


class RobustnessConditionType(str, Enum):
    REPLAY = "REPLAY"
    NOISE = "NOISE"
    REVERBERATION = "REVERBERATION"
    COMPRESSION = "COMPRESSION"
    CLIPPING = "CLIPPING"
    SYNTHETIC_VARIATION = "SYNTHETIC_VARIATION"
    PERTURBATION = "PERTURBATION"


@dataclass
class RobustnessCondition:
    condition_id: str
    condition_type: str              # RobustnessConditionType enum string
    severity: str                    # LOW, MEDIUM, HIGH, SEVERE
    parameters: Dict[str, Any]
    source_audio_id: str
    description: str


@dataclass
class ComparisonDelta:
    synthetic_score_delta: float
    replay_score_delta: float
    risk_score_delta: float
    confidence_delta: float
    decision_before: str
    decision_after: str
    decision_changed: bool
    evidence_added_count: int
    evidence_removed_count: int


@dataclass
class RobustnessResult:
    condition_id: str
    condition_type: str
    severity: str
    parameters: Dict[str, Any]
    source_audio_id: str
    baseline_synthetic_score: float
    transformed_synthetic_score: float
    baseline_replay_score: float
    transformed_replay_score: float
    baseline_risk_score: float
    transformed_risk_score: float
    baseline_confidence: float
    transformed_confidence: float
    baseline_decision: str
    transformed_decision: str
    delta: ComparisonDelta
    baseline_latency_ms: float
    transformed_latency_ms: float
    transformation_latency_ms: float
    total_latency_ms: float
    timestamp: str = field(default_factory=lambda: time.strftime("%Y-%m-%d %H:%M:%S"))


@dataclass
class RobustnessAssessment:
    overall_status: str              # ROBUSTNESS_ENGINE_VERIFIED
    conditions_evaluated: int
    conditions_stable_count: int
    stability_ratio: float           # [0.0 - 1.0]
    mean_transformation_latency_ms: float
    results: List[Dict[str, Any]]
    disclosures: List[str]
