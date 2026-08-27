"""
Explanation Builder Module.
Renders formatted decision explanation summaries.
"""

from typing import Dict, Any
from app.services.explainability.types import DecisionExplanation


def build_explanation_text(explanation: DecisionExplanation) -> str:
    lines = [
        "============================================================",
        "VOXSHIELD DECISION EXPLAINABILITY REPORT",
        "============================================================",
        f"Decision:           {explanation.decision}",
        f"Risk Score:         {explanation.risk_score} / 100.0",
        f"Confidence State:   {explanation.confidence_state} ({explanation.confidence_indicator})",
        f"Scientific Status:  {explanation.claim_status}",
        "------------------------------------------------------------",
        "PRIMARY SUPPORTING EVIDENCE (RANKED):"
    ]

    if explanation.primary_evidence:
        for ev in explanation.primary_evidence:
            lines.append(f" #{ev['rank']} [{ev['category']}] (Score: {ev['evidence_score']}) — {ev['explanation']}")
    else:
        lines.append("  (None)")

    lines.append("\nCONTRADICTORY COUNTER-EVIDENCE:")
    if explanation.counter_evidence:
        for cev in explanation.counter_evidence:
            lines.append(f" [-] {cev['explanation']}")
    else:
        lines.append("  (None)")

    lines.append("\nLIMITATIONS & DISCLOSURES:")
    if explanation.limitations:
        for lim in explanation.limitations:
            lines.append(f" [!] {lim}")
    else:
        lines.append("  (None)")

    lines.append("============================================================")
    return "\n".join(lines)
