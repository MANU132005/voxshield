import pytest
from app.services.evaluation.benchmark_gate import BenchmarkGate
from app.services.evaluation.types import BenchmarkGateStatus


def test_missing_conditions_blocks_certification():
    gate = BenchmarkGate()
    status, info = gate.certify_benchmark(
        dataset_ready=False,
        checkpoint_valid=True,
        provenance_real=False,
        leakage_free=True,
        real_evaluation_completed=False,
        sample_count=0
    )

    assert status == BenchmarkGateStatus.BLOCKED
    assert info["certified"] is False


def test_all_conditions_passed_issues_certified():
    gate = BenchmarkGate()
    status, info = gate.certify_benchmark(
        dataset_ready=True,
        checkpoint_valid=True,
        provenance_real=True,
        leakage_free=True,
        real_evaluation_completed=True,
        sample_count=500
    )

    assert status == BenchmarkGateStatus.CERTIFIED
    assert info["certified"] is True
