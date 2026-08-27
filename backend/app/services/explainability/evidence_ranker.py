"""
Deterministic Evidence Ranker Module.

Ranks evidence items based on evidence_score = normalized_strength * reliability.
Exposes evidence_rank, evidence_score, supporting_signals, and rationale.
"""

from dataclasses import asdict
from typing import Dict, Any, List
from app.services.explainability.types import RankedEvidence


def rank_evidence_items(evidence_dicts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    ranked_list: List[RankedEvidence] = []

    for ev in evidence_dicts:
        strength = float(ev.get("normalized_strength", 0.5))
        reliability = float(ev.get("reliability", 0.8))
        ev_score = round(strength * reliability, 4)

        ranked_list.append(RankedEvidence(
            evidence_id=ev.get("id", "EV_UNKNOWN"),
            rank=0,
            category=ev.get("category", "UNKNOWN"),
            signal=ev.get("signal", "unknown_signal"),
            strength=strength,
            reliability=reliability,
            evidence_score=ev_score,
            explanation=ev.get("explanation", "")
        ))

    # Sort descending by evidence_score
    ranked_list.sort(key=lambda x: x.evidence_score, reverse=True)

    # Assign ranks
    result: List[Dict[str, Any]] = []
    for idx, item in enumerate(ranked_list, start=1):
        item.rank = idx
        result.append(asdict(item))

    return result
