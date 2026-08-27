"""
Scientific Claim Gate Module.
Integrates with ClaimGuard to determine claim statuses for M17 claims.
"""

from typing import Dict, Any
from app.services.model_integrity.claim_guard import ClaimGuard, ClaimStatus


class ClaimGate:
    def __init__(self, dataset_available: bool = False, real_model_trained: bool = False):
        self.guard = ClaimGuard(dataset_available=dataset_available, real_model_trained=real_model_trained)

    def evaluate_claims(self) -> Dict[str, str]:
        m17_keys = [
            "architecture_pipeline",
            "feature_extraction_pipeline",
            "dsp_replay_engine",
            "forensic_engine_architecture",
            "latency_measurement",
            "asvspoof_2019_accuracy",
            "asvspoof_2019_eer",
            "asvspoof_real_benchmark",
            "model_calibration",
            "benchmark_certification"
        ]
        return {key: self.guard.classify_claim(key).value for key in m17_keys}
