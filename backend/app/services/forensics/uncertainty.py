"""
Uncertainty Engine.

Evaluates measurement confidence and assigns an uncalibrated confidence_indicator
with explicit confidence_basis statements. Does NOT claim statistical probability.
"""

from typing import Dict, Any, List, Tuple
import numpy as np

from app.services.forensics.types import EvidenceItem, EvidenceDirection


def evaluate_uncertainty(
    signal_duration_sec: float,
    evidence_items: List[EvidenceItem],
    model_provenance: str
) -> Tuple[float, List[str]]:
    confidence = 0.85
    basis: List[str] = []

    # 1. Duration Impact
    if signal_duration_sec < 0.8:
        confidence -= 0.20
        basis.append(f"Short audio duration ({round(signal_duration_sec, 2)}s) reduces feature extraction stability.")
    elif signal_duration_sec >= 1.5:
        basis.append("Sufficient audio duration (>1.5s) supports stable feature extraction.")

    # 2. Checkpoint Provenance Disclosure Impact
    if model_provenance == "DEMO_DSP_SYNTHETIC_DATASET":
        confidence -= 0.15
        basis.append("Neural model checkpoint trained on DSP demo signals; uncalibrated for real-world voice clones.")

    # 3. Evidence Direction Agreement
    spoof_count = sum(1 for ev in evidence_items if ev.direction == EvidenceDirection.SUPPORTS_SPOOF.value)
    genuine_count = sum(1 for ev in evidence_items if ev.direction == EvidenceDirection.SUPPORTS_GENUINE.value)

    if spoof_count > 0 and genuine_count == 0:
        confidence += 0.05
        basis.append("Multiple independent forensic signals consistently support spoof classification.")
    elif spoof_count > 0 and genuine_count > 0:
        confidence -= 0.10
        basis.append("Conflicting evidence observed across spectral and signal integrity indicators.")

    # Bound confidence_indicator strictly in [0.10, 0.95]
    confidence_indicator = round(max(0.10, min(0.95, confidence)), 2)
    return confidence_indicator, basis
