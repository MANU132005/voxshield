import os
import json
import pytest
import numpy as np

from app.services.model_integrity.auditor import audit_model_checkpoint, calculate_file_sha256
from app.services.model_integrity.claim_guard import ClaimGuard, ClaimStatus
from scripts.evaluate_real_world import calculate_eer, evaluate_real_world


def test_checkpoint_audit_integrity():
    audit_res = audit_model_checkpoint("./models/anti_spoofing_resnet.pt")

    assert "checkpoint_found" in audit_res
    assert "sha256_hash" in audit_res
    assert audit_res["nan_detected"] is False
    assert audit_res["inf_detected"] is False
    assert "provenance" in audit_res


def test_missing_checkpoint_returns_blocked():
    audit_res = audit_model_checkpoint("./non_existent_model_checkpoint.pt")

    assert audit_res["checkpoint_found"] is False
    assert audit_res["sha256_hash"] == "NOT_FOUND"
    assert "BLOCKED" in audit_res["status"]


def test_sha256_hash_calculation():
    sha = calculate_file_sha256("./models/anti_spoofing_resnet.pt")
    assert isinstance(sha, str)
    assert len(sha) == 64  # SHA-256 length is 64 hex chars


def test_claim_guard_status_classification():
    guard = ClaimGuard(dataset_available=False, real_model_trained=False)

    assert guard.classify_claim("architecture_pipeline") == ClaimStatus.VERIFIED
    assert guard.classify_claim("latency_measurement") == ClaimStatus.MEASURED
    assert guard.classify_claim("risk_engine_fusion") == ClaimStatus.INFERRED
    assert guard.classify_claim("asvspoof_2019_accuracy") == ClaimStatus.BLOCKED


def test_eer_calculation_math_validity():
    # Perfectly separated genuine (0) and spoof (1) scores
    labels = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    scores = np.array([0.1, 0.2, 0.15, 0.05, 0.85, 0.9, 0.95, 0.8])

    eer, threshold = calculate_eer(labels, scores)

    assert eer == 0.0
    assert 0.15 <= threshold <= 0.85


def test_eer_calculation_overlapping_scores():
    labels = np.array([0, 0, 1, 1])
    scores = np.array([0.2, 0.8, 0.2, 0.8])  # 50% overlap

    eer, threshold = calculate_eer(labels, scores)

    assert 0.0 <= eer <= 1.0


def test_evaluate_real_world_missing_dataset_returns_blocked():
    res = evaluate_real_world(dataset_root="./non_existent_dataset_directory_xyz")

    assert "BLOCKED" in res["status"]
    assert res["metrics"]["accuracy"] == "N/A"
    assert res["metrics"]["eer"] == "N/A"
    assert os.path.exists("reports/m13_real_world_metrics.json")


def test_sih_claim_matrix_structure():
    claims = ClaimGuard.get_sih_claim_matrix()

    assert "SAFE_TO_CLAIM" in claims
    assert "NOT_SAFE_TO_CLAIM" in claims
    assert len(claims["SAFE_TO_CLAIM"]) >= 3
    assert len(claims["NOT_SAFE_TO_CLAIM"]) >= 3


def test_m13_report_files_exist():
    assert os.path.exists("reports/m13_model_integrity_audit.md")
    assert os.path.exists("reports/m13_model_integrity.json")
    assert os.path.exists("reports/m13_evaluation_status.md")
    assert os.path.exists("reports/m13_evaluation_status.json")
    assert os.path.exists("reports/m13_robustness_report.md")
    assert os.path.exists("reports/m13_failure_analysis.md")
    assert os.path.exists("reports/m13_model_card.md")
    assert os.path.exists("reports/m13_final_report.md")
