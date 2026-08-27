"""
Detector Disagreement Engine Module.

Analyzes cross-detector agreement/disagreement across Neural, Replay, Forensic, and Generalization detectors.
"""

from dataclasses import asdict
from typing import Dict, Any, List
from app.services.live_detection.types import DetectorAgreementState, DetectorAgreementResult


class DetectorAgreementEngine:
    def analyze_agreement(
        self,
        neural_score: float,
        replay_score: float,
        forensic_score: float,
        generalization_score: float
    ) -> DetectorAgreementResult:

        scores = {
            "neural_detector": neural_score,
            "replay_dsp_detector": replay_score,
            "forensic_engine": forensic_score,
            "generalization_extractor": generalization_score
        }

        spoof_detectors = [k for k, v in scores.items() if v >= 0.50]
        genuine_detectors = [k for k, v in scores.items() if v < 0.50]

        if len(spoof_detectors) >= 3:
            state = DetectorAgreementState.HIGH_AGREEMENT.value
            agreed = spoof_detectors
            disagreed = genuine_detectors
            dominant = "NEURAL_SPOOF" if neural_score >= 0.65 else "ACOUSTIC_REPLAY"
            exp = f"Unanimous spoof agreement across {len(spoof_detectors)} detection modules."
        elif len(genuine_detectors) >= 3:
            state = DetectorAgreementState.HIGH_AGREEMENT.value
            agreed = genuine_detectors
            disagreed = spoof_detectors
            dominant = "NATURAL_SPEECH"
            exp = f"Unanimous genuine agreement across {len(genuine_detectors)} detection modules."
        elif len(spoof_detectors) == 2 and len(genuine_detectors) == 2:
            state = DetectorAgreementState.DETECTOR_DISAGREEMENT.value
            agreed = spoof_detectors
            disagreed = genuine_detectors
            dominant = "CONFLICTING_SIGNALS"
            exp = "Detector disagreement: 2 modules report spoof indicators while 2 report genuine characteristics."
        else:
            state = DetectorAgreementState.MODERATE_AGREEMENT.value
            agreed = spoof_detectors if len(spoof_detectors) > len(genuine_detectors) else genuine_detectors
            disagreed = genuine_detectors if len(spoof_detectors) > len(genuine_detectors) else spoof_detectors
            dominant = "NEURAL_SPOOF" if neural_score >= 0.50 else "NATURAL_SPEECH"
            exp = "Moderate agreement across detection modules."

        return DetectorAgreementResult(
            agreement_state=state,
            agreed_detectors=agreed,
            disagreeing_detectors=disagreed,
            dominant_evidence_type=dominant,
            explanation=exp
        )
