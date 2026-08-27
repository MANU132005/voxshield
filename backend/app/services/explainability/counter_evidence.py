"""
Counter-Evidence Engine.

Searches explicitly for contradictory evidence that challenges a tentative decision.
If decision = LIKELY_SPOOF, searches for clean natural characteristics.
If decision = LIKELY_GENUINE, searches for subtle synthetic or replay artifacts.
"""

from dataclasses import asdict
from typing import Dict, Any, List
from app.services.explainability.types import CounterEvidenceItem


def evaluate_counter_evidence(
    decision: str,
    evidence_dicts: List[Dict[str, Any]],
    counter_evidence_dicts: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    items: List[CounterEvidenceItem] = []

    if decision in ("LIKELY_SPOOF", "SUSPICIOUS", "HIGH_RISK"):
        # Search for natural features that contradict spoof hypothesis
        for item in counter_evidence_dicts:
            items.append(CounterEvidenceItem(
                signal=item.get("signal", "genuine_indicator"),
                finding=item.get("explanation", "Natural acoustic property observed."),
                impact_on_confidence=-0.08,
                explanation=f"Contradictory genuine evidence: {item.get('explanation', '')}"
            ))

        # Check if no clipping or heavy distortion is present
        clipping_found = any(e.get("signal") == "clipping_ratio" for e in evidence_dicts)
        if not clipping_found:
            items.append(CounterEvidenceItem(
                signal="clipping_absent",
                finding="No digital clipping saturation observed.",
                impact_on_confidence=-0.05,
                explanation="Absence of digital waveform clipping indicates un-overdriven recording."
            ))

    elif decision == "LIKELY_GENUINE":
        # Search for subtle spoof anomalies that contradict genuine hypothesis
        for item in evidence_dicts:
            items.append(CounterEvidenceItem(
                signal=item.get("signal", "spoof_indicator"),
                finding=item.get("explanation", "Minor anomaly observed."),
                impact_on_confidence=-0.10,
                explanation=f"Contradictory spoof indicator: {item.get('explanation', '')}"
            ))

    return [asdict(i) for i in items]
