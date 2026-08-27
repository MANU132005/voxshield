import os
import json
import pytest
from app.services.evaluation.dataset_gate import DatasetGate
from app.services.evaluation.checkpoint_gate import CheckpointGate
from app.services.evaluation.types import DatasetGateStatus, CheckpointGateStatus, BenchmarkGateStatus
from app.services.evaluation.claim_gate import ClaimGate


def test_m18_dataset_discovery_halts_real_training():
    ds_gate = DatasetGate()
    status, info = ds_gate.verify_dataset("./datasets/non_existent_ASVspoof2019_LA/LA")

    assert status == DatasetGateStatus.DATASET_MISSING
    assert info["dataset_found"] is False


def test_m18_checkpoint_provenance_preserved():
    ckpt_gate = CheckpointGate()
    status, info = ckpt_gate.verify_checkpoint("./models/anti_spoofing_resnet.pt")

    assert status == CheckpointGateStatus.PROVENANCE_BLOCKED
    assert info["provenance"] == "DEMO_DSP_SYNTHETIC_DATASET"


def test_m18_claim_gate_blocks_benchmark_claims():
    claim_gate = ClaimGate(dataset_available=False, real_model_trained=False)
    claims = claim_gate.evaluate_claims()

    assert claims["asvspoof_2019_accuracy"] == "BLOCKED"
    assert claims["asvspoof_2019_eer"] == "BLOCKED"
    assert claims["asvspoof_real_benchmark"] == "BLOCKED"
    assert claims["benchmark_certification"] == "BLOCKED"


def test_m18_all_reports_generated():
    m18_reports = [
        "reports/m18_dataset_status.md",
        "reports/m18_dataset_status.json",
        "reports/m18_training_config.md",
        "reports/m18_training_metrics.json",
        "reports/m18_validation_report.md",
        "reports/m18_real_benchmark.md",
        "reports/m18_attack_analysis.md",
        "reports/m18_robustness_report.md",
        "reports/m18_calibration_report.md",
        "reports/m18_model_comparison.md",
        "reports/m18_claim_gate_report.md",
        "reports/m18_reproducibility_report.md",
        "reports/m18_security_audit.md",
        "reports/M18_IMPLEMENTATION_REPORT.md"
    ]

    for r in m18_reports:
        assert os.path.exists(r), f"Missing M18 report: {r}"

    # Verify JSON content
    with open("reports/m18_training_metrics.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        assert data["status"] in ("BLOCKED", "COMPLETED")
