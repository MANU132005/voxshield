import pytest
from app.services.evaluation.checkpoint_gate import CheckpointGate
from app.services.evaluation.types import CheckpointGateStatus


def test_missing_checkpoint_returns_missing_status():
    gate = CheckpointGate()
    status, info = gate.verify_checkpoint("./non_existent_checkpoint.pt")

    assert status == CheckpointGateStatus.CHECKPOINT_MISSING
    assert info["checkpoint_found"] is False


def test_demo_checkpoint_returns_provenance_blocked():
    gate = CheckpointGate()
    status, info = gate.verify_checkpoint("./models/anti_spoofing_resnet.pt")

    assert status == CheckpointGateStatus.PROVENANCE_BLOCKED
    assert info["provenance"] == "DEMO_DSP_SYNTHETIC_DATASET"
