"""
Benchmark Gate Module.

Central certification authority. Issued CERTIFIED only when all 8 scientific conditions pass.
Otherwise issues BLOCKED.
"""

from typing import Dict, Any, Tuple
from app.services.evaluation.types import BenchmarkGateStatus


class BenchmarkGate:
    def certify_benchmark(
        self,
        dataset_ready: bool,
        checkpoint_valid: bool,
        provenance_real: bool,
        leakage_free: bool,
        real_evaluation_completed: bool,
        sample_count: int
    ) -> Tuple[BenchmarkGateStatus, Dict[str, Any]]:

        checks = {
            "dataset_ready": dataset_ready,
            "checkpoint_valid": checkpoint_valid,
            "provenance_real": provenance_real,
            "leakage_free": leakage_free,
            "real_evaluation_completed": real_evaluation_completed,
            "sufficient_samples": sample_count > 100
        }

        all_passed = all(checks.values())
        if all_passed:
            return BenchmarkGateStatus.CERTIFIED, {"certified": True, "checks": checks}

        return BenchmarkGateStatus.BLOCKED, {"certified": False, "checks": checks, "reason": "One or more certification conditions failed."}
