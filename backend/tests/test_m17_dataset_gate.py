import pytest
from app.services.evaluation.dataset_gate import DatasetGate
from app.services.evaluation.types import DatasetGateStatus


def test_missing_dataset_returns_missing_status():
    gate = DatasetGate()
    status, info = gate.verify_dataset("./non_existent_dataset_directory_123")

    assert status == DatasetGateStatus.DATASET_MISSING
    assert info["dataset_found"] is False


def test_dataset_gate_handles_invalid_root():
    gate = DatasetGate()
    status, info = gate.verify_dataset("C:/invalid/path/xyz")

    assert status == DatasetGateStatus.DATASET_MISSING
