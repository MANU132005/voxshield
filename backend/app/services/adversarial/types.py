"""
Adversarial Audio Test Framework — Data Types & Models.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional


class PerturbationType(str, Enum):
    GAUSSIAN_NOISE = "GAUSSIAN_NOISE"
    BACKGROUND_NOISE = "BACKGROUND_NOISE"
    HIGH_FREQ_NOISE = "HIGH_FREQ_NOISE"
    LOW_FREQ_RUMBLE = "LOW_FREQ_RUMBLE"
    DYNAMIC_COMPRESSION = "DYNAMIC_COMPRESSION"
    HARD_CLIPPING = "HARD_CLIPPING"
    GAIN_AMPLIFICATION = "GAIN_AMPLIFICATION"
    GAIN_ATTENUATION = "GAIN_ATTENUATION"
    RESAMPLING_DOWN_UP = "RESAMPLING_DOWN_UP"
    BAND_LIMITING = "BAND_LIMITING"
    SILENCE_INSERTION = "SILENCE_INSERTION"
    POP_TRANSIENT_INSERTION = "POP_TRANSIENT_INSERTION"
    REVERBERATION_SIMULATION = "REVERBERATION_SIMULATION"
    CODEC_DEGRADATION = "CODEC_DEGRADATION"
    COMBINED_PERTURBATION = "COMBINED_PERTURBATION"


@dataclass
class PerturbationCase:
    case_id: str
    attack_type: str
    parameters: Dict[str, Any]
    expected_effect: str


@dataclass
class AdversarialResult:
    case_id: str
    attack_type: str
    parameters: Dict[str, Any]
    expected_effect: str
    observed_effect: str
    risk_score_before: float
    risk_score_after: float
    confidence_before: float
    confidence_after: float
    decision_before: str
    decision_after: str
    claim_status: str = "INFERRED"
