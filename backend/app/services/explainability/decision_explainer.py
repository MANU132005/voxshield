"""
Decision Explainer Module.

Maps raw detector and forensic outputs into structured explanations with explicit
confidence states (HIGH_MEASUREMENT_CONFIDENCE, MODERATE, LOW, INSUFFICIENT).
"""

from dataclasses import asdict
from typing import Dict, Any, List
from app.services.explainability.types import DecisionExplanation, ConfidenceState
from app.services.explainability.evidence_ranker import rank_evidence_items
from app.services.explainability.counter_evidence import evaluate_counter_evidence


class DecisionExplainer:
    def explain_decision(
        self,
        decision: str,
        risk_score: float,
        confidence_indicator: float,
        evidence_dicts: List[Dict[str, Any]],
        counter_evidence_dicts: List[Dict[str, Any]],
        limitations: List[str],
        claim_status: str = "INFERRED"
    ) -> DecisionExplanation:
        # Determine Confidence State
        if confidence_indicator >= 0.80:
            conf_state = ConfidenceState.HIGH_MEASUREMENT_CONFIDENCE.value
        elif confidence_indicator >= 0.60:
            conf_state = ConfidenceState.MODERATE_MEASUREMENT_CONFIDENCE.value
        elif confidence_indicator >= 0.40:
            conf_state = ConfidenceState.LOW_MEASUREMENT_CONFIDENCE.value
        else:
            conf_state = ConfidenceState.INSUFFICIENT_EVIDENCE.value

        # Rank primary evidence
        ranked_primary = rank_evidence_items(evidence_dicts)

        # Evaluate counter evidence
        evaluated_counter = evaluate_counter_evidence(decision, evidence_dicts, counter_evidence_dicts)

        # Build Summary Text
        summary = (
            f"Decision: {decision} (Risk Score: {risk_score}/100.0, Confidence: {conf_state}). "
            f"Identified {len(ranked_primary)} primary spoof indicators and {len(evaluated_counter)} counter-evidence items. "
            f"Scientific Claim Status: {claim_status}."
        )

        return DecisionExplanation(
            decision=decision,
            risk_score=risk_score,
            confidence_state=conf_state,
            confidence_indicator=confidence_indicator,
            primary_evidence=ranked_primary,
            counter_evidence=evaluated_counter,
            limitations=limitations,
            claim_status=claim_status,
            summary_text=summary
        )
