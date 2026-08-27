"""
Adversarial Perturbation Engine.
Applies perturbation cases to audio signals deterministically.
"""

import numpy as np
from typing import Dict, Any, List
from app.services.adversarial.types import PerturbationCase, PerturbationType
from app.services.adversarial.attack_generators import apply_perturbation_by_type


class PerturbationEngine:
    def create_standard_test_cases(self) -> List[PerturbationCase]:
        return [
            PerturbationCase(
                case_id="ADV_01_GAUSSIAN_NOISE",
                attack_type=PerturbationType.GAUSSIAN_NOISE.value,
                parameters={"snr_db": 15.0},
                expected_effect="Moderate reduction in signal SNR and spectral stationarity."
            ),
            PerturbationCase(
                case_id="ADV_02_HARD_CLIPPING",
                attack_type=PerturbationType.HARD_CLIPPING.value,
                parameters={"threshold": 0.70},
                expected_effect="Waveform saturation triggering signal integrity clipping evidence."
            ),
            PerturbationCase(
                case_id="ADV_03_RESAMPLING_8KHZ",
                attack_type=PerturbationType.RESAMPLING_DOWN_UP.value,
                parameters={"target_sr": 8000},
                expected_effect="Narrow-band anti-aliasing filtering above 4 kHz."
            ),
            PerturbationCase(
                case_id="ADV_04_HIGH_FREQ_NOISE",
                attack_type=PerturbationType.HIGH_FREQ_NOISE.value,
                parameters={"noise_amp": 0.08},
                expected_effect="High frequency spectral energy concentration."
            ),
            PerturbationCase(
                case_id="ADV_05_POP_TRANSIENT",
                attack_type=PerturbationType.POP_TRANSIENT_INSERTION.value,
                parameters={"location": 0.5, "pop_amp": 0.99},
                expected_effect="Single sample impulse spike triggering crest factor anomaly."
            )
        ]

    def perturb_signal(self, signal: np.ndarray, p_case: PerturbationCase) -> np.ndarray:
        return apply_perturbation_by_type(signal, p_case.attack_type, p_case.parameters)
