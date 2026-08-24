"""
Risk Assessment Engine.

Combines synthetic speech probabilities and replay attack vectors
into aggregated threat categories (SAFE, SUSPICIOUS, HIGH_RISK).
"""

from typing import Dict, Any, List

class RiskEngine:
    def __init__(
        self, 
        synthetic_weight: float = 0.6, 
        replay_weight: float = 0.4,
        safe_threshold: float = 0.35,
        high_risk_threshold: float = 0.70
    ):
        self.synthetic_weight = synthetic_weight
        self.replay_weight = replay_weight
        self.safe_threshold = safe_threshold
        self.high_risk_threshold = high_risk_threshold

    def evaluate(self, synthetic_score: float, replay_score: float) -> Dict[str, Any]:
        risk_score = round(
            (synthetic_score * self.synthetic_weight) + (replay_score * self.replay_weight), 
            2
        )
        
        reasons: List[str] = []

        if synthetic_score >= 0.70:
            reasons.append("Synthetic voice characteristics detected")
        elif synthetic_score >= 0.40:
            reasons.append("Elevated synthetic voice probability")

        if replay_score >= 0.65:
            reasons.append("Possible replay characteristics detected")
        elif replay_score >= 0.40:
            reasons.append("Minor acoustic reverberation anomalies")

        if risk_score >= self.high_risk_threshold:
            status = "HIGH_RISK"
        elif risk_score >= self.safe_threshold:
            status = "SUSPICIOUS"
        else:
            status = "SAFE"
            if not reasons:
                reasons.append("Acoustic features align with natural human voice")

        return {
            "synthetic_score": round(synthetic_score, 2),
            "replay_score": round(replay_score, 2),
            "speaker_match": None,  # Speaker verification is planned for Phase 2
            "risk_score": risk_score,
            "status": status,
            "reasons": reasons
        }
