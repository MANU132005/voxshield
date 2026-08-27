"""
Production-Grade Risk Engine & Multi-Modal Threat Evaluator.

Combines AI synthetic voice clone scores, acoustic replay attack DSP indicators,
and signal quality metrics into a unified, explainable VoxShield security assessment.
Uses a 6-layer multi-signal fusion model with defensive numerical protection.
"""

import math
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Union
import numpy as np

from app.services.anti_spoofing.detector import AntiSpoofingResult
from app.services.replay_detection.dsp import ReplayDetectionResult
from app.services.audio.processor import ProcessedAudio


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Verdict(str, Enum):
    AUTHENTIC = "AUTHENTIC"
    SUSPICIOUS = "SUSPICIOUS"
    SPOOF_SUSPECTED = "SPOOF_SUSPECTED"
    REPLAY_SUSPECTED = "REPLAY_SUSPECTED"
    HIGH_RISK = "HIGH_RISK"


@dataclass
class EvidenceItem:
    code: str                           # e.g., "SYNTHETIC_VOICE_HIGH"
    category: str                       # "synthetic_voice", "replay_attack", "signal_anomaly", "low_quality"
    severity: str                       # "low", "medium", "high", "critical"
    observed_value: float               # Measured numerical value
    threshold: float                    # Decision threshold
    message: str                        # Explanation string


@dataclass
class RiskAssessment:
    risk_score: float                   # Overall risk score [0.0 - 100.0]
    risk_level: str                     # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    verdict: str                        # "AUTHENTIC", "SUSPICIOUS", "SPOOF_SUSPECTED", etc.
    attack_indicators: List[str]        # List of active attack types
    confidence: float                   # Assessment confidence [0.0 - 1.0]
    evidence: List[Dict[str, Any]]      # Machine-readable evidence objects
    reasons: List[str]                  # Human-readable explanations
    contributing_signals: Dict[str, Any]# Full signal breakdown
    evaluator_version: str              # "risk_engine_v1.0"


def _sanitize_float(val: Any, default: float = 0.0, min_val: float = 0.0, max_val: float = 1.0) -> float:
    """Sanitizes numerical inputs handling None, NaN, Inf, and out-of-bound values safely."""
    if val is None:
        return default
    try:
        f_val = float(val)
        if math.isnan(f_val) or math.isinf(f_val):
            return default
        return float(np.clip(f_val, min_val, max_val))
    except (ValueError, TypeError):
        return default


class RiskEvaluator:
    """
    Multi-Modal VoxShield Threat Evaluator.

    Executes layered threat fusion combining AI synthetic probabilities,
    acoustic replay DSP indicators, and audio signal quality metrics into a
    numerically safe, explainable security assessment.
    """
    def __init__(
        self,
        synthetic_weight: float = 60.0,
        replay_weight: float = 40.0,
        quality_weight: float = 10.0,
        evaluator_version: str = "risk_engine_v1.0"
    ):
        self.synthetic_weight = synthetic_weight
        self.replay_weight = replay_weight
        self.quality_weight = quality_weight
        self.evaluator_version = evaluator_version

    def evaluate_risk(
        self,
        synthetic_input: Union[float, AntiSpoofingResult, None] = None,
        replay_input: Union[float, ReplayDetectionResult, None] = None,
        processed_audio: Optional[ProcessedAudio] = None
    ) -> RiskAssessment:
        """
        Executes layered threat evaluation with defensive signal validation.
        Guarantees risk_score in [0.0, 100.0] and confidence in [0.0, 1.0].
        """
        # 1. LAYER 1: DEFENSIVE SIGNAL EXTRACTION & SANITIZATION
        if isinstance(synthetic_input, AntiSpoofingResult):
            raw_synth = synthetic_input.synthetic_score
            synth_conf = synthetic_input.confidence
            synth_version = synthetic_input.model_version
        else:
            raw_synth = _sanitize_float(synthetic_input, default=0.0)
            synth_conf = 0.85 if synthetic_input is not None else 0.50
            synth_version = "raw_score_v1.0"

        synth_score = _sanitize_float(raw_synth, default=0.0)
        synth_conf = _sanitize_float(synth_conf, default=0.50)

        replay_indicators: List[str] = []
        if isinstance(replay_input, ReplayDetectionResult):
            raw_replay = replay_input.replay_score
            replay_conf = replay_input.confidence
            replay_indicators = replay_input.triggered_indicators
        else:
            raw_replay = _sanitize_float(replay_input, default=0.0)
            replay_conf = 0.80 if replay_input is not None else 0.50

        replay_score = _sanitize_float(raw_replay, default=0.0)
        replay_conf = _sanitize_float(replay_conf, default=0.50)

        # 2. LAYER 2: AUDIO QUALITY & SATURATION ANALYSIS
        clipping_ratio = 0.0
        if processed_audio is not None and processed_audio.audio_signal is not None:
            sig = processed_audio.audio_signal
            if len(sig) > 0:
                clipping_ratio = float(np.sum(np.abs(sig) >= 0.99) / len(sig))

        clipping_ratio = _sanitize_float(clipping_ratio, default=0.0)
        quality_penalty = 0.0
        if clipping_ratio > 0.01:
            quality_penalty = 0.50
        elif clipping_ratio > 0.001:
            quality_penalty = 0.25

        # 3. LAYER 3 & 4: COMPONENT THREAT CONTRIBUTIONS
        synth_contrib = synth_score * self.synthetic_weight
        replay_contrib = replay_score * self.replay_weight
        quality_contrib = quality_penalty * self.quality_weight

        # 4. LAYER 5: CROSS-SIGNAL MULTI-THREAT SYNERGISTIC BOOST
        multi_threat_boost = 0.0
        if synth_score >= 0.50 and replay_score >= 0.35:
            multi_threat_boost = 15.0  # Synergistic risk boost when AI clone AND replay are both present

        raw_total_risk = synth_contrib + replay_contrib + quality_contrib + multi_threat_boost
        risk_score = float(round(np.clip(raw_total_risk, 0.0, 100.0), 2))

        # Overall System Confidence Calculation
        overall_conf = float(round(np.clip(0.5 * (synth_conf + replay_conf), 0.0, 1.0), 4))

        # 5. LAYER 6: EVIDENCE GENERATION & REASONS
        evidence_items: List[EvidenceItem] = []
        reasons: List[str] = []
        attack_indicators: List[str] = []

        if synth_score >= 0.70:
            attack_indicators.append("synthetic_voice")
            reasons.append("Synthetic voice characteristics detected")
            evidence_items.append(EvidenceItem(
                code="SYNTHETIC_VOICE_HIGH",
                category="synthetic_voice",
                severity="high",
                observed_value=round(synth_score, 4),
                threshold=0.70,
                message="Strong synthetic-voice neural pattern detected."
            ))
        elif synth_score >= 0.40:
            attack_indicators.append("synthetic_voice")
            reasons.append("Elevated synthetic voice probability")
            evidence_items.append(EvidenceItem(
                code="SYNTHETIC_VOICE_MODERATE",
                category="synthetic_voice",
                severity="medium",
                observed_value=round(synth_score, 4),
                threshold=0.40,
                message="Moderate synthetic-voice indicators present."
            ))

        if replay_score >= 0.65:
            attack_indicators.append("replay_attack")
            reasons.append("Possible replay characteristics detected")
            evidence_items.append(EvidenceItem(
                code="REPLAY_ATTACK_HIGH",
                category="replay_attack",
                severity="high",
                observed_value=round(replay_score, 4),
                threshold=0.65,
                message="Strong acoustic replay attack indicators detected."
            ))
        elif replay_score >= 0.40:
            attack_indicators.append("replay_attack")
            reasons.append("Minor acoustic reverberation anomalies")
            evidence_items.append(EvidenceItem(
                code="REPLAY_ATTACK_MODERATE",
                category="replay_attack",
                severity="medium",
                observed_value=round(replay_score, 4),
                threshold=0.40,
                message="Moderate acoustic replay indicators present."
            ))

        # Include specific DSP acoustic replay reasons
        for r_reason in replay_indicators:
            if r_reason not in reasons:
                reasons.append(r_reason)

        if clipping_ratio > 0.001:
            attack_indicators.append("signal_anomaly")
            evidence_items.append(EvidenceItem(
                code="SIGNAL_CLIPPING_SATURATION",
                category="signal_anomaly",
                severity="medium",
                observed_value=round(clipping_ratio, 5),
                threshold=0.001,
                message="Signal clipping saturation detected."
            ))

        if multi_threat_boost > 0.0:
            evidence_items.append(EvidenceItem(
                code="COMBINED_MULTI_THREAT",
                category="multi_threat",
                severity="critical",
                observed_value=round(multi_threat_boost, 2),
                threshold=15.0,
                message="Simultaneous AI voice clone and acoustic replay indicators detected."
            ))

        # Determine Risk Level & Verdict
        if synth_score >= 0.70 and replay_score >= 0.65:
            risk_level = RiskLevel.CRITICAL
            verdict = Verdict.HIGH_RISK
        elif synth_score >= 0.70:
            risk_level = RiskLevel.HIGH
            verdict = Verdict.SPOOF_SUSPECTED
        elif replay_score >= 0.65:
            risk_level = RiskLevel.HIGH
            verdict = Verdict.REPLAY_SUSPECTED
        elif risk_score >= 75.0:
            risk_level = RiskLevel.CRITICAL
            verdict = Verdict.HIGH_RISK
        elif risk_score >= 55.0:
            risk_level = RiskLevel.HIGH
            if synth_score >= replay_score:
                verdict = Verdict.SPOOF_SUSPECTED
            else:
                verdict = Verdict.REPLAY_SUSPECTED
        elif risk_score >= 30.0 or synth_score >= 0.40 or replay_score >= 0.40:
            risk_level = RiskLevel.MEDIUM
            verdict = Verdict.SUSPICIOUS
        else:
            risk_level = RiskLevel.LOW
            verdict = Verdict.AUTHENTIC
            if not reasons:
                reasons.append("Acoustic features align with natural human voice")

        # Serialized evidence items
        serialized_evidence = [item.__dict__ for item in evidence_items]

        return RiskAssessment(
            risk_score=risk_score,
            risk_level=risk_level.value,
            verdict=verdict.value,
            attack_indicators=list(set(attack_indicators)),
            confidence=overall_conf,
            evidence=serialized_evidence,
            reasons=reasons,
            contributing_signals={
                "synthetic_score": round(synth_score, 4),
                "synthetic_confidence": round(synth_conf, 4),
                "synthetic_version": synth_version,
                "replay_score": round(replay_score, 4),
                "replay_confidence": round(replay_conf, 4),
                "clipping_ratio": round(clipping_ratio, 5),
                "multi_threat_boost": round(multi_threat_boost, 2)
            },
            evaluator_version=self.evaluator_version
        )


class RiskEngine(RiskEvaluator):
    """
    Backward-compatible adapter class for existing VoxShield API routes and tests.
    """
    def __init__(
        self,
        synthetic_weight: float = 0.6,
        replay_weight: float = 0.4,
        safe_threshold: float = 0.35,
        high_risk_threshold: float = 0.70
    ):
        super().__init__(
            synthetic_weight=synthetic_weight * 100.0,
            replay_weight=replay_weight * 100.0
        )
        self.safe_threshold = safe_threshold
        self.high_risk_threshold = high_risk_threshold

    def evaluate(self, synthetic_score: float, replay_score: float) -> Dict[str, Any]:
        assessment = self.evaluate_risk(synthetic_input=synthetic_score, replay_input=replay_score)

        # Map risk_score [0-100] back to legacy [0.0 - 1.0] scale
        legacy_risk_score = round(assessment.risk_score / 100.0, 2)

        if legacy_risk_score >= self.high_risk_threshold:
            status = "HIGH_RISK"
        elif legacy_risk_score >= self.safe_threshold:
            status = "SUSPICIOUS"
        else:
            status = "SAFE"

        return {
            "synthetic_score": round(assessment.contributing_signals["synthetic_score"], 2),
            "replay_score": round(assessment.contributing_signals["replay_score"], 2),
            "speaker_match": None,
            "risk_score": legacy_risk_score,
            "status": status,
            "reasons": assessment.reasons
        }
