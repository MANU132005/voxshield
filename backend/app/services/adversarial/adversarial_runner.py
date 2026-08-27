"""
Adversarial Runner Module.
Executes perturbation scenarios against the ForensicEngine and collects results.
"""

from dataclasses import asdict
from typing import Dict, Any, List
import numpy as np

from app.services.adversarial.types import PerturbationCase, AdversarialResult
from app.services.adversarial.perturbation_engine import PerturbationEngine
from app.services.forensics.forensic_engine import ForensicEngine


class AdversarialRunner:
    def __init__(self, forensic_engine: ForensicEngine = None):
        self.forensic_engine = forensic_engine or ForensicEngine()
        self.perturbation_engine = PerturbationEngine()

    def run_adversarial_suite(
        self,
        clean_signal: np.ndarray,
        sample_rate: int = 16000,
        baseline_synth_score: float = 0.50,
        baseline_replay_score: float = 0.20
    ) -> List[Dict[str, Any]]:
        baseline_assessment = self.forensic_engine.evaluate_forensics(
            baseline_synth_score, baseline_replay_score, clean_signal, sample_rate
        )

        test_cases = self.perturbation_engine.create_standard_test_cases()
        results: List[Dict[str, Any]] = []

        for case in test_cases:
            perturbed_signal = self.perturbation_engine.perturb_signal(clean_signal, case)

            # Evaluate perturbed audio
            perturbed_assessment = self.forensic_engine.evaluate_forensics(
                baseline_synth_score, baseline_replay_score, perturbed_signal, sample_rate
            )

            res = AdversarialResult(
                case_id=case.case_id,
                attack_type=case.attack_type,
                parameters=case.parameters,
                expected_effect=case.expected_effect,
                observed_effect=f"Risk changed from {baseline_assessment.risk_score} to {perturbed_assessment.risk_score}",
                risk_score_before=baseline_assessment.risk_score,
                risk_score_after=perturbed_assessment.risk_score,
                confidence_before=baseline_assessment.confidence_indicator,
                confidence_after=perturbed_assessment.confidence_indicator,
                decision_before=baseline_assessment.decision,
                decision_after=perturbed_assessment.decision,
                claim_status="INFERRED"
            )

            results.append(asdict(res))

        return results
