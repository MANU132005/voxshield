"""
Attack Taxonomy Classifier.

Classifies evidence into non-definitive attack hypotheses:
- AI_SYNTHESIS_SUSPECTED
- VOICE_CONVERSION_SUSPECTED
- REPLAY_SUSPECTED
- SIGNAL_PROCESSING_SUSPECTED
- UNKNOWN_SPOOF_PATTERN
- NO_STRONG_SPOOF_EVIDENCE
"""

from typing import Dict, Any, List
from app.services.forensics.types import EvidenceItem, AttackHypothesis, EvidenceDirection, ScientificStatus


def classify_attack_hypotheses(
    synthetic_score: float,
    replay_score: float,
    evidence_items: List[EvidenceItem]
) -> List[AttackHypothesis]:
    hypotheses: List[AttackHypothesis] = []
    ev_ids = {ev.id: ev for ev in evidence_items}

    # 1. AI Synthesis Hypothesis
    if synthetic_score >= 0.65 or "EV_SPEC_STATIONARY" in ev_ids or "EV_CONSIST_SYNTHETIC_OVER_REGULARITY" in ev_ids:
        supporting = [ev_id for ev_id in ["EV_SPEC_STATIONARY", "EV_CONSIST_SYNTHETIC_OVER_REGULARITY", "EV_SPEC_FLAT_LOW"] if ev_id in ev_ids]
        hypotheses.append(AttackHypothesis(
            classification="AI_SYNTHESIS_SUSPECTED",
            supporting_evidence=supporting,
            confidence_indicator=round(max(synthetic_score, 0.60), 2),
            claim_status=ScientificStatus.INFERRED.value
        ))

    # 2. Replay Hypothesis
    if replay_score >= 0.50 or any("REPLAY" in ev.category for ev in evidence_items):
        hypotheses.append(AttackHypothesis(
            classification="REPLAY_SUSPECTED",
            supporting_evidence=["EV_REPLAY_INDICATOR"],
            confidence_indicator=round(max(replay_score, 0.50), 2),
            claim_status=ScientificStatus.INFERRED.value
        ))

    # 3. Signal Processing Hypothesis
    if "EV_INTEG_CLIPPING_SEVERE" in ev_ids or "EV_INTEG_DC_OFFSET" in ev_ids:
        supporting = [ev_id for ev_id in ["EV_INTEG_CLIPPING_SEVERE", "EV_INTEG_DC_OFFSET"] if ev_id in ev_ids]
        hypotheses.append(AttackHypothesis(
            classification="SIGNAL_PROCESSING_SUSPECTED",
            supporting_evidence=supporting,
            confidence_indicator=0.75,
            claim_status=ScientificStatus.MEASURED.value
        ))

    # 4. No Strong Spoof Evidence Hypothesis
    if not hypotheses and synthetic_score < 0.35 and replay_score < 0.35:
        hypotheses.append(AttackHypothesis(
            classification="NO_STRONG_SPOOF_EVIDENCE",
            supporting_evidence=[],
            confidence_indicator=0.85,
            claim_status=ScientificStatus.INFERRED.value
        ))

    return hypotheses
