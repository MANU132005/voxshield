import os
import json
import pytest

from app.services.dataset_discovery.types import DatasetStatus, DatasetAuditResult
from app.services.dataset_discovery.discovery import DatasetDiscoveryEngine
from app.services.dataset_discovery.leakage_checker import DataLeakageChecker
from app.services.model_integrity.claim_guard import ClaimGuard
from app.services.evaluation.benchmark_gate import BenchmarkGate


def test_phase6_missing_dataset_audit():
    engine = DatasetDiscoveryEngine(dataset_root="non_existent_path/LA")
    res = engine.audit_dataset()

    assert isinstance(res, DatasetAuditResult)
    assert res.status == DatasetStatus.BLOCKED_DATASET.value
    assert res.is_valid is False
    assert res.total_audio_files == 0
    assert res.total_protocol_entries == 0


def test_phase6_speaker_leakage_detection():
    checker = DataLeakageChecker()
    train_spk = {"LA_0001", "LA_0002", "LA_0003"}
    dev_spk = {"LA_0003", "LA_0004"}
    eval_spk = {"LA_0005"}

    has_leakage, details = checker.check_speaker_leakage(train_spk, dev_spk, eval_spk)
    assert has_leakage is True
    assert len(details) == 1
    assert "Speaker leakage" in details[0]


def test_phase6_audio_hash_leakage_detection():
    checker = DataLeakageChecker()
    train_hash = {"hash_a", "hash_b"}
    dev_hash = {"hash_b"}
    eval_hash = {"hash_c"}

    has_leakage, details = checker.check_audio_hash_leakage(train_hash, dev_hash, eval_hash)
    assert has_leakage is True
    assert "Audio payload leakage" in details[0]


def test_phase6_model_checkpoint_provenance_leakage():
    checker = DataLeakageChecker()
    prov_demo = {"model_provenance": "DEMO_DSP_SYNTHETIC_DATASET"}

    has_leakage, details = checker.check_model_checkpoint_leakage(prov_demo)
    assert has_leakage is True
    assert "Model provenance leakage" in details[0]


def test_phase6_claim_guard_enforcement():
    cg = ClaimGuard(dataset_available=False, real_model_trained=False)
    allowed = cg.verify_claim("ASVspoof 2019 Certified 99% EER")

    assert allowed is False


def test_phase6_report_files_generation():
    from scripts.run_phase6_benchmark import main
    main([])

    reports_dir = os.path.abspath("./reports")
    assert os.path.exists(os.path.join(reports_dir, "phase6_dataset_audit.md"))
    assert os.path.exists(os.path.join(reports_dir, "phase6_dataset_status.json"))
    assert os.path.exists(os.path.join(reports_dir, "phase6_training_report.md"))
    assert os.path.exists(os.path.join(reports_dir, "phase6_evaluation_report.md"))
    assert os.path.exists(os.path.join(reports_dir, "phase6_benchmark_report.md"))
    assert os.path.exists(os.path.join(reports_dir, "PHASE6_FINAL_REPORT.md"))
