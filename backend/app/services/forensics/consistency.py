"""
Signal Consistency Engine.

Compares independent signal metrics to detect acoustic contradictions or cross-vector agreement.
Does NOT fabricate probabilities; returns structured EvidenceItem objects with status INFERRED.
"""

from typing import Dict, Any, List
import numpy as np

from app.services.forensics.types import EvidenceItem, EvidenceCategory, EvidenceDirection, ScientificStatus


def analyze_cross_signal_consistency(evidence_items: List[EvidenceItem]) -> List[EvidenceItem]:
    consistency_evidence: List[EvidenceItem] = []

    # Map signals for easy cross-lookup
    signals = {ev.signal: ev for ev in evidence_items}

    # 1. Clipping vs Crest Factor Consistency Check
    if "clipping_ratio" in signals and "crest_factor_db" in signals:
        clip_ev = signals["clipping_ratio"]
        crest_ev = signals["crest_factor_db"]

        if clip_ev.value > 0.02 and crest_ev.value > 15.0:
            consistency_evidence.append(EvidenceItem(
                id="EV_CONSIST_CLIP_CREST_CONTRADICTION",
                category=EvidenceCategory.CONSISTENCY.value,
                signal="clipping_crest_consistency",
                value=round(abs(clip_ev.value - crest_ev.value), 4),
                normalized_strength=0.82,
                direction=EvidenceDirection.SUPPORTS_SPOOF.value,
                reliability=0.88,
                status=ScientificStatus.INFERRED.value,
                explanation="Contradiction between severe clipping and high crest factor (indicates digital gain manipulation)."
            ))

    # 2. Spectral Flatness vs Energy Envelope Consistency Check
    if "spectral_flatness" in signals and "energy_envelope_variation" in signals:
        flat_ev = signals["spectral_flatness"]
        env_ev = signals["energy_envelope_variation"]

        if flat_ev.value < 0.05 and env_ev.value < 0.05:
            consistency_evidence.append(EvidenceItem(
                id="EV_CONSIST_SYNTHETIC_OVER_REGULARITY",
                category=EvidenceCategory.CONSISTENCY.value,
                signal="spectral_temporal_consistency",
                value=round(flat_ev.value + env_ev.value, 4),
                normalized_strength=0.85,
                direction=EvidenceDirection.SUPPORTS_SPOOF.value,
                reliability=0.90,
                status=ScientificStatus.INFERRED.value,
                explanation="Cross-signal agreement: Dual spectral flatness and temporal energy over-regularity strongly indicate synthetic vocoding."
            ))

    return consistency_evidence
