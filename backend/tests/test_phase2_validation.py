import os
import json
import pytest
from app.services.evaluation.dataset_gate import DatasetGate
from app.services.evaluation.checkpoint_gate import CheckpointGate
from app.services.evaluation.types import DatasetGateStatus, CheckpointGateStatus
from app.services.evaluation.claim_gate import ClaimGate


def test_phase2_dataset_discovery_halts_training():
    ds_gate = DatasetGate()
    status, info = ds_gate.verify_dataset("./datasets/non_existent_ASVspoof2019_LA/LA")

    assert status == DatasetGateStatus.DATASET_MISSING
    assert info["dataset_found"] is False


def test_phase2_baseline_checkpoint_preserved():
    ckpt_gate = CheckpointGate()
    status, info = ckpt_gate.verify_checkpoint("./models/anti_spoofing_resnet.pt")

    assert status == CheckpointGateStatus.PROVENANCE_BLOCKED
    assert info["provenance"] == "DEMO_DSP_SYNTHETIC_DATASET"


def test_phase2_claim_gate_blocks_benchmark_claims():
    claim_gate = ClaimGate(dataset_available=False, real_model_trained=False)
    claims = claim_gate.evaluate_claims()

    assert claims["asvspoof_2019_accuracy"] == "BLOCKED"
    assert claims["asvspoof_2019_eer"] == "BLOCKED"
    assert claims["asvspoof_real_benchmark"] == "BLOCKED"
    assert claims["benchmark_certification"] == "BLOCKED"


def test_phase2_all_reports_generated():
    reports = [
        "reports/phase2_dataset_blocked.md",
        "reports/phase2_dataset_report.md",
        "reports/phase2_dataset_status.json",
        "reports/phase2_leakage_audit.md",
        "reports/phase2_leakage_audit.json",
        "reports/phase2_training_report.md",
        "reports/phase2_training_report.json",
        "reports/phase2_evaluation_report.md",
        "reports/phase2_evaluation_report.json",
        "reports/phase2_metrics.md",
        "reports/phase2_calibration_report.md",
        "reports/phase2_benchmark_certification.md",
        "reports/PHASE2_FINAL_REPORT.md"
    ]

    for r in reports:
        assert os.path.exists(r), f"Missing Phase 2 report: {r}"

    # Verify JSON content
    with open("reports/phase2_training_report.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        assert data["status"] == "BLOCKED"
        assert data["training_executed"] is False
        assert data["baseline_checkpoint_preserved"] is True
