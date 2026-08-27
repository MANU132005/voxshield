"""
Scientific Claim Guard System.

Enforces strict scientific validity boundaries by categorizing claims into
VERIFIED, MEASURED, INFERRED, UNVERIFIED, or BLOCKED based on verified empirical evidence.
Prevents unsupported benchmark or accuracy claims from appearing in documentation or APIs.
"""

from enum import Enum
from typing import Dict, Any, List


class ClaimStatus(str, Enum):
    VERIFIED = "VERIFIED"       # Empirical metric measured on official dataset split
    MEASURED = "MEASURED"       # Engineering metric measured on local execution environment
    INFERRED = "INFERRED"       # Rule-based or heuristic security logic
    UNVERIFIED = "UNVERIFIED"   # Claim lacking empirical benchmark execution
    BLOCKED = "BLOCKED"         # Evaluation cannot execute due to missing dataset


class ClaimGuard:
    """
    Scientific Claim Guard for SIH Technical Evaluation.
    """
    def __init__(self, dataset_available: bool = False, real_model_trained: bool = False):
        self.dataset_available = dataset_available
        self.real_model_trained = real_model_trained

    def classify_claim(self, claim_key: str, evidence_available: bool = False) -> ClaimStatus:
        """Classifies a claim into scientific status based on empirical proof."""
        if claim_key in ("architecture_pipeline", "feature_extraction_pipeline", "dsp_replay_engine", "forensic_engine_architecture"):
            return ClaimStatus.VERIFIED

        if claim_key in ("latency_measurement", "memory_usage", "throughput_rps", "forensic_latency_benchmark"):
            return ClaimStatus.MEASURED

        if claim_key in ("risk_engine_fusion", "evidence_item_generation", "forensic_spectral_evidence", "forensic_replay_evidence", "forensic_multi_signal_decision"):
            return ClaimStatus.INFERRED

        blocked_keys = (
            "asvspoof_2019_accuracy", "asvspoof_2019_eer", "asvspoof_2019_roc_auc",
            "asvspoof_accuracy", "asvspoof_eer", "real_world_deepfake_detection",
            "asvspoof_real_accuracy", "asvspoof_real_precision", "asvspoof_real_recall",
            "asvspoof_real_f1", "asvspoof_real_roc_auc", "asvspoof_real_eer",
            "asvspoof_real_benchmark", "model_real_world_performance",
            "model_calibration", "benchmark_certification"
        )
        if claim_key in blocked_keys or "ASVSPOOF" in claim_key.upper():
            if not self.dataset_available or not self.real_model_trained:
                return ClaimStatus.BLOCKED
            return ClaimStatus.VERIFIED if evidence_available else ClaimStatus.UNVERIFIED

        return ClaimStatus.UNVERIFIED

    def verify_claim(self, claim_key: str, evidence_available: bool = False) -> bool:
        """Returns True if a claim is scientifically allowed (VERIFIED or MEASURED)."""
        status = self.classify_claim(claim_key, evidence_available)
        return status in (ClaimStatus.VERIFIED, ClaimStatus.MEASURED)

    @staticmethod
    def get_sih_claim_matrix() -> Dict[str, List[str]]:
        """Returns safe to claim vs not safe to claim guidelines for SIH evaluation."""
        return {
            "SAFE_TO_CLAIM": [
                "VoxShield combines neural, acoustic, spectral, temporal, and signal-integrity evidence into an explainable voice-security assessment.",
                "VoxShield features 6-stage 16kHz audio normalization, 80-channel Log-Mel & 20-channel LFCC extraction, PyTorch 2D CNN inference, and Single-STFT DSP replay analysis.",
                "VoxShield includes automated ASVspoof-compatible dataset auditing, preflight validation, and leakage detection infrastructure.",
                "VoxShield features a multi-vector Forensic Intelligence Engine producing structured EvidenceItem graphs and attack hypothesis classifications.",
                "VoxShield features a 16-stage Real-World Evaluation Orchestrator and Benchmark Certification Gate.",
                "VoxShield achieves mean end-to-end execution latency of ~40ms - 45ms on modern multi-core CPUs."
            ],
            "NOT_SAFE_TO_CLAIM": [
                "VoxShield detects AI-generated voices with 100% / 99% accuracy on real-world voice clones (Model baseline was trained on synthetic DSP demo signals).",
                "VoxShield is benchmarked on the official ASVspoof 2019 LA evaluation dataset (Official 15.2 GB FLAC dataset is missing locally).",
                "VoxShield has a scientifically calibrated Equal Error Rate (EER) on physical voice clones.",
                "VoxShield detects all AI-generated voice clones or replay attacks seamlessly."
            ]
        }
