import os
import pytest
import numpy as np

from scripts.audit_asvspoof import audit_asvspoof_dataset
from app.services.model_integrity.auditor import audit_model_checkpoint
from app.services.model_integrity.claim_guard import ClaimGuard, ClaimStatus
from scripts.evaluate_real_world import calculate_eer, evaluate_real_world


def test_demo_checkpoint_preservation():
    audit_res = audit_model_checkpoint("./models/anti_spoofing_resnet.pt")

    assert audit_res["checkpoint_found"] is True
    assert audit_res["provenance"] == "DEMO_DSP_SYNTHETIC_DATASET"
    assert audit_res["num_batches_tracked"] == 72


def test_real_checkpoint_separate_path():
    real_path = "./models/anti_spoofing_asvspoof2019_la.pt"
    audit_res = audit_model_checkpoint(real_path)

    # Real checkpoint is not created yet because real dataset training was blocked
    assert audit_res["checkpoint_found"] is False
    assert "BLOCKED" in audit_res["status"]


def test_dataset_missing_blocks_training_and_evaluation():
    audit_res = audit_asvspoof_dataset(root_path="./non_existent_asvspoof_dataset")

    assert audit_res["dataset_found"] is False
    assert "BLOCKED" in audit_res["status"]


def test_evaluate_real_world_no_synthetic_fallback():
    eval_res = evaluate_real_world(dataset_root="./non_existent_asvspoof_dataset")

    assert eval_res["status"] == "BLOCKED — REAL ASVSPOOF DATASET NOT PRESENT"
    assert eval_res["metrics"]["accuracy"] == "N/A"
    assert eval_res["metrics"]["eer"] == "N/A"


def test_claim_guard_m14_rules():
    guard = ClaimGuard(dataset_available=False, real_model_trained=False)

    assert guard.classify_claim("asvspoof_2019_accuracy") == ClaimStatus.BLOCKED
    assert guard.classify_claim("asvspoof_2019_eer") == ClaimStatus.BLOCKED
    assert guard.classify_claim("architecture_pipeline") == ClaimStatus.VERIFIED


def test_m14_report_artifacts_exist():
    reports = [
        "reports/m14_dataset_preflight.json",
        "reports/m14_dataset_preflight.md",
        "reports/m14_training_config.json",
        "reports/m14_training_report.json",
        "reports/m14_training_report.md",
        "reports/m14_checkpoint_audit.json",
        "reports/m14_checkpoint_audit.md",
        "reports/m14_evaluation.json",
        "reports/m14_evaluation.md",
        "reports/m14_failure_analysis.md",
        "reports/m14_robustness.md",
        "reports/m14_benchmark.json",
        "reports/m14_benchmark_report.md",
        "reports/m14_demo_vs_real_model.md",
        "reports/m14_claims.md",
        "reports/m14_final_report.md"
    ]
    for r in reports:
        assert os.path.exists(r), f"Missing report: {r}"
