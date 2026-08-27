"""
Explainability Engine — Data Types & Models.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


class ConfidenceState(str, Enum):
    HIGH_MEASUREMENT_CONFIDENCE = "HIGH_MEASUREMENT_CONFIDENCE"
    MODERATE_MEASUREMENT_CONFIDENCE = "MODERATE_MEASUREMENT_CONFIDENCE"
    LOW_MEASUREMENT_CONFIDENCE = "LOW_MEASUREMENT_CONFIDENCE"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


@dataclass
class RankedEvidence:
    evidence_id: str
    rank: int
    category: str
    signal: str
    strength: float
    reliability: float
    evidence_score: float
    explanation: str


@dataclass
class CounterEvidenceItem:
    signal: str
    finding: str
    impact_on_confidence: float
    explanation: str


@dataclass
class DecisionExplanation:
    decision: str
    risk_score: float
    confidence_state: str
    confidence_indicator: float
    primary_evidence: List[Dict[str, Any]]
    counter_evidence: List[Dict[str, Any]]
    limitations: List[str]
    claim_status: str
    summary_text: str
