"""
VoxShield Forensic Engine Aggregator.

Orchestrates multi-vector forensic evaluation, cross-signal consistency, uncertainty estimation,
attack hypothesis classification, and forensic report rendering.
"""

from dataclasses import asdict
from typing import Dict, Any, List, Optional
import numpy as np

from app.services.forensics.types import (
    EvidenceItem,
    EvidenceCategory,
    EvidenceDirection,
    ScientificStatus,
    ForensicDecision,
    ForensicAssessment
)
from app.services.forensics.spectral_forensics import analyze_spectral_forensics
from app.services.forensics.temporal_forensics import analyze_temporal_forensics
from app.services.forensics.signal_integrity import analyze_signal_integrity
from app.services.forensics.consistency import analyze_cross_signal_consistency
from app.services.forensics.uncertainty import evaluate_uncertainty
from app.services.forensics.attack_taxonomy import classify_attack_hypotheses
from app.services.forensics.report import generate_forensic_report


class ForensicEngine:
    """
    VoxShield Forensic Intelligence Engine.
    """
    def __init__(self, model_provenance: str = "DEMO_DSP_SYNTHETIC_DATASET"):
        self.model_provenance = model_provenance

    def evaluate_forensics(
        self,
        synthetic_score: float,
        replay_score: float,
        signal: np.ndarray,
        sample_rate: int = 16000
    ) -> ForensicAssessment:
        all_evidence: List[EvidenceItem] = []

        # 1. Neural Evidence Item
        if synthetic_score >= 0.60:
            all_evidence.append(EvidenceItem(
                id="EV_NEURAL_SPOOF_HIGH",
                category=EvidenceCategory.NEURAL.value,
                signal="synthetic_score",
                value=round(synthetic_score, 4),
                normalized_strength=round(synthetic_score, 4),
                direction=EvidenceDirection.SUPPORTS_SPOOF.value,
                reliability=0.80,
                status=ScientificStatus.INFERRED.value,
                explanation=f"Neural 2D CNN inference indicates high synthetic likelihood ({round(synthetic_score * 100, 1)}%)."
            ))

        # 2. Replay Evidence Item
        if replay_score >= 0.50:
            all_evidence.append(EvidenceItem(
                id="EV_REPLAY_INDICATOR_HIGH",
                category=EvidenceCategory.REPLAY.value,
                signal="replay_score",
                value=round(replay_score, 4),
                normalized_strength=round(replay_score, 4),
                direction=EvidenceDirection.SUPPORTS_SPOOF.value,
                reliability=0.85,
                status=ScientificStatus.INFERRED.value,
                explanation=f"Single-STFT DSP analysis indicates acoustic replay indicators ({round(replay_score * 100, 1)}%)."
            ))

        # 3. Spectral, Temporal, Integrity Forensics
        all_evidence.extend(analyze_spectral_forensics(signal, sample_rate))
        all_evidence.extend(analyze_temporal_forensics(signal, sample_rate))
        all_evidence.extend(analyze_signal_integrity(signal, sample_rate))

        # 4. Cross-Signal Consistency
        all_evidence.extend(analyze_cross_signal_consistency(all_evidence))

        # Separate Evidence vs Counter-Evidence
        spoof_evidence = [asdict(ev) for ev in all_evidence if ev.direction == EvidenceDirection.SUPPORTS_SPOOF.value]
        genuine_evidence = [asdict(ev) for ev in all_evidence if ev.direction == EvidenceDirection.SUPPORTS_GENUINE.value]

        # 5. Risk Score Computation
        base_risk = (synthetic_score * 0.45 + replay_score * 0.35) * 100.0
        forensic_bonus = min(20.0, len(spoof_evidence) * 4.0)
        risk_score = round(max(0.0, min(100.0, base_risk + forensic_bonus)), 1)

        if risk_score >= 70.0:
            risk_level = "HIGH"
            decision = ForensicDecision.LIKELY_SPOOF.value
        elif risk_score >= 40.0:
            risk_level = "MEDIUM"
            decision = ForensicDecision.SUSPICIOUS.value
        elif replay_score >= 0.60:
            risk_level = "MEDIUM"
            decision = ForensicDecision.REPLAY_SUSPECTED.value
        else:
            risk_level = "LOW"
            decision = ForensicDecision.LIKELY_GENUINE.value

        # Support INCONCLUSIVE for low SNR or very short audio
        duration_sec = len(signal) / float(sample_rate) if len(signal) > 0 else 0.0
        if duration_sec < 0.6:
            decision = ForensicDecision.INCONCLUSIVE.value

        # 6. Uncertainty & Confidence Indicator
        conf_ind, conf_basis = evaluate_uncertainty(duration_sec, all_evidence, self.model_provenance)

        # 7. Attack Hypotheses Classification
        hypotheses = [asdict(h) for h in classify_attack_hypotheses(synthetic_score, replay_score, all_evidence)]

        # 8. Limitations & Disclosures
        limitations = [
            "Official ASVspoof 2019 benchmark evaluation is currently BLOCKED (Dataset missing locally).",
            "Neural model checkpoint provenance is synthetic DSP demo signals; scores are uncalibrated likelihoods."
        ]

        assessment = ForensicAssessment(
            decision=decision,
            risk_score=risk_score,
            risk_level=risk_level,
            confidence_indicator=conf_ind,
            confidence_basis=conf_basis,
            attack_hypotheses=hypotheses,
            evidence=spoof_evidence,
            counter_evidence=genuine_evidence,
            limitations=limitations,
            claim_status=ScientificStatus.INFERRED.value,
            forensic_report=""
        )

        assessment.forensic_report = generate_forensic_report(asdict(assessment))
        return assessment
