"""
Temporal Multi-Window Evidence Fusion & Stability Module.

Fuses structured evidence across temporal audio windows, measuring timeline stability and preventing single-frame anomaly dominance.
"""

import numpy as np
from dataclasses import asdict
from typing import Dict, Any, List, Tuple
from app.services.live_detection.types import (
    LiveWindow,
    TemporalStabilityState,
    TemporalStabilityResult,
    LiveConfidenceState
)


class TemporalFusionEngine:
    def analyze_temporal_stability(self, windows: List[LiveWindow]) -> TemporalStabilityResult:
        if not windows:
            return TemporalStabilityResult(
                stability_state=TemporalStabilityState.INSUFFICIENT_TIMELINE.value,
                variance_score=0.0,
                consecutive_agreements=0,
                window_count=0,
                explanation="Insufficient audio duration to establish temporal timeline."
            )

        if len(windows) == 1:
            w = windows[0]
            st = TemporalStabilityState.STABLE_SPOOF.value if w.risk_score >= 50.0 else TemporalStabilityState.STABLE_GENUINE.value
            return TemporalStabilityResult(
                stability_state=st,
                variance_score=0.0,
                consecutive_agreements=1,
                window_count=1,
                explanation="Single analysis window evaluated."
            )

        scores = [w.risk_score for w in windows]
        var = float(np.var(scores))

        spoof_wins = [w for w in windows if w.risk_score >= 50.0]
        genuine_wins = [w for w in windows if w.risk_score < 50.0]

        max_consec = 1
        curr_consec = 1
        for i in range(1, len(windows)):
            if (windows[i].risk_score >= 50.0) == (windows[i-1].risk_score >= 50.0):
                curr_consec += 1
                max_consec = max(max_consec, curr_consec)
            else:
                curr_consec = 1

        if len(spoof_wins) == len(windows):
            state = TemporalStabilityState.STABLE_SPOOF.value
            exp = f"Stable spoof indicators consistently observed across all {len(windows)} temporal windows."
        elif len(genuine_wins) == len(windows):
            state = TemporalStabilityState.STABLE_GENUINE.value
            exp = f"Stable genuine characteristics consistently observed across all {len(windows)} temporal windows."
        elif len(windows) >= 3 and (len(spoof_wins) == 1 or len(genuine_wins) == 1):
            state = TemporalStabilityState.TRANSIENT_ANOMALY.value
            exp = f"Transient anomaly detected in 1 window out of {len(windows)} total windows."
        else:
            state = TemporalStabilityState.CONFLICTING_TIMELINE.value
            exp = f"Conflicting timeline: {len(spoof_wins)} windows spoof, {len(genuine_wins)} windows genuine."

        return TemporalStabilityResult(
            stability_state=state,
            variance_score=round(var, 2),
            consecutive_agreements=max_consec,
            window_count=len(windows),
            explanation=exp
        )

    def fuse_multi_window_assessment(
        self,
        windows: List[LiveWindow],
        stability: TemporalStabilityResult,
        agreement_state: str
    ) -> Tuple[float, float, str, str]:

        if not windows:
            return 0.0, 0.0, LiveConfidenceState.INSUFFICIENT_EVIDENCE.value, "INCONCLUSIVE"

        weights = np.linspace(0.8, 1.2, len(windows))
        weights /= np.sum(weights)

        risk_scores = np.array([w.risk_score for w in windows])
        fused_risk = float(np.sum(risk_scores * weights))

        synth_scores = np.array([w.synthetic_score for w in windows])
        fused_synth = float(np.sum(synth_scores * weights))

        if agreement_state == "DETECTOR_DISAGREEMENT" or stability.stability_state == TemporalStabilityState.CONFLICTING_TIMELINE.value:
            conf_state = LiveConfidenceState.CONFLICTED.value
            conf_score = 0.40
        elif stability.stability_state in (TemporalStabilityState.STABLE_SPOOF.value, TemporalStabilityState.STABLE_GENUINE.value):
            conf_state = LiveConfidenceState.SUPPORTED.value
            conf_score = round(float(np.mean([w.confidence for w in windows])), 4)
        else:
            conf_state = LiveConfidenceState.SUPPORTED.value
            conf_score = round(float(np.mean([w.confidence for w in windows])) * 0.85, 4)

        if fused_risk >= 70.0:
            decision = "LIKELY_SPOOF"
        elif fused_risk >= 35.0:
            decision = "SUSPICIOUS"
        else:
            decision = "LIKELY_GENUINE"

        return round(fused_risk, 2), round(fused_synth, 4), conf_state, decision
