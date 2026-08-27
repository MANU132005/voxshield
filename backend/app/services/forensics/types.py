"""
VoxShield Forensic Intelligence Engine — Data Types & Enums.

Defines structured models for evidence items, evidence categories, evidence directions,
scientific statuses, attack hypotheses, and comprehensive forensic assessments.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


class EvidenceCategory(str, Enum):
    NEURAL = "NEURAL"
    REPLAY = "REPLAY"
    SPECTRAL = "SPECTRAL"
    TEMPORAL = "TEMPORAL"
    INTEGRITY = "INTEGRITY"
    CONSISTENCY = "CONSISTENCY"
    QUALITY = "QUALITY"
    ARTIFACT = "ARTIFACT"


class EvidenceDirection(str, Enum):
    SUPPORTS_SPOOF = "SUPPORTS_SPOOF"
    SUPPORTS_GENUINE = "SUPPORTS_GENUINE"
    INCONCLUSIVE = "INCONCLUSIVE"


class ScientificStatus(str, Enum):
    VERIFIED = "VERIFIED"
    MEASURED = "MEASURED"
    INFERRED = "INFERRED"
    UNVERIFIED = "UNVERIFIED"
    BLOCKED = "BLOCKED"


class ForensicDecision(str, Enum):
    LIKELY_GENUINE = "LIKELY_GENUINE"
    SUSPICIOUS = "SUSPICIOUS"
    LIKELY_SPOOF = "LIKELY_SPOOF"
    REPLAY_SUSPECTED = "REPLAY_SUSPECTED"
    INCONCLUSIVE = "INCONCLUSIVE"


@dataclass
class EvidenceItem:
    id: str                             # Unique evidence ID (e.g. EV_SPEC_FLAT_01)
    category: str                       # EvidenceCategory enum value
    signal: str                         # Name of measured signal
    value: float                        # Raw measured numerical value
    normalized_strength: float          # Bounded evidence magnitude [0.0 - 1.0]
    direction: str                      # EvidenceDirection enum value
    reliability: float                  # Signal measurement reliability [0.0 - 1.0]
    status: str                         # ScientificStatus enum value
    explanation: str                    # Human-readable explanation string


@dataclass
class AttackHypothesis:
    classification: str                 # e.g., AI_SYNTHESIS_SUSPECTED, REPLAY_SUSPECTED
    supporting_evidence: List[str]      # List of evidence IDs supporting hypothesis
    confidence_indicator: float         # Confidence magnitude [0.0 - 1.0]
    claim_status: str                   # ScientificStatus enum value


@dataclass
class ForensicAssessment:
    decision: str                       # ForensicDecision enum value
    risk_score: float                   # Overall risk score [0.0 - 100.0]
    risk_level: str                     # LOW, MEDIUM, HIGH, CRITICAL
    confidence_indicator: float         # Overall confidence indicator [0.0 - 1.0]
    confidence_basis: List[str]         # Explanations for confidence assignment
    attack_hypotheses: List[Dict[str, Any]] # List of AttackHypothesis dicts
    evidence: List[Dict[str, Any]]      # List of EvidenceItem dicts supporting spoof
    counter_evidence: List[Dict[str, Any]] # List of EvidenceItem dicts supporting genuine
    limitations: List[str]              # Documented scientific limitations
    claim_status: str                   # Overall scientific claim status
    forensic_report: str                # Formatted ASCII/Markdown forensic report string
