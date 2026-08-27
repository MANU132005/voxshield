import os
import pytest
from app.services.evaluation.evaluation_orchestrator import EvaluationOrchestrator


def test_orchestrator_blocked_pipeline_execution():
    orchestrator = EvaluationOrchestrator()
    res = orchestrator.run_orchestration(
        dataset_root="./non_existent_dataset_directory",
        checkpoint_path="./models/anti_spoofing_resnet.pt"
    )

    assert res.overall_status == "BLOCKED"
    assert res.benchmark_certification == "BLOCKED"
    assert res.dataset_status == "DATASET_MISSING"
    assert res.checkpoint_status == "PROVENANCE_BLOCKED"
    assert res.metrics is None
    assert len(res.stages) == 16


def test_m17_report_files_generated():
    reports = [
        "reports/m17_evaluation_report.md",
        "reports/m17_evaluation_status.json",
        "reports/m17_benchmark_gate.md",
        "reports/m17_metric_integrity.md",
        "reports/m17_calibration_report.md",
        "reports/m17_claim_gate_report.md",
        "reports/m17_reproducibility_report.md",
        "reports/M17_IMPLEMENTATION_REPORT.md"
    ]
    for r in reports:
        assert os.path.exists(r), f"Missing report: {r}"
