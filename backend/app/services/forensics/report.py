"""
Forensic Report Generator.

Renders structured ASCII/Markdown forensic evaluation reports from ForensicAssessment objects.
"""

from typing import Dict, Any


def generate_forensic_report(assessment_dict: Dict[str, Any]) -> str:
    decision = assessment_dict.get("decision", "INCONCLUSIVE")
    risk_score = assessment_dict.get("risk_score", 0.0)
    risk_level = assessment_dict.get("risk_level", "LOW")
    conf_ind = assessment_dict.get("confidence_indicator", 0.5)
    claim_status = assessment_dict.get("claim_status", "INFERRED")

    evidence_list = assessment_dict.get("evidence", [])
    counter_list = assessment_dict.get("counter_evidence", [])
    limitations = assessment_dict.get("limitations", [])

    lines = [
        "------------------------------------------------------------",
        "VOXSHIELD FORENSIC ASSESSMENT REPORT",
        "------------------------------------------------------------",
        f"Decision:             {decision}",
        f"Risk Score:           {risk_score} / 100.0 ({risk_level})",
        f"Confidence Indicator: {conf_ind}",
        f"Scientific Claim:     {claim_status}",
        "------------------------------------------------------------",
        "EVIDENCE (SUPPORTS SPOOF):"
    ]

    if evidence_list:
        for ev in evidence_list:
            lines.append(f" [+] [{ev['category']}] {ev['explanation']}")
    else:
        lines.append("  (None)")

    lines.append("\nCOUNTER-EVIDENCE (SUPPORTS GENUINE):")
    if counter_list:
        for ev in counter_list:
            lines.append(f" [-] [{ev['category']}] {ev['explanation']}")
    else:
        lines.append("  (None)")

    lines.append("\nLIMITATIONS & DISCLOSURES:")
    if limitations:
        for lim in limitations:
            lines.append(f" [!] {lim}")
    else:
        lines.append("  (None)")

    lines.append("------------------------------------------------------------")
    return "\n".join(lines)
