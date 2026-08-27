import os
import json
import pytest
import numpy as np

from app.services.anti_spoofing.generalization import GeneralizationExtractor, GeneralizationArtifacts


def test_generalization_extractor_clean_signal():
    extractor = GeneralizationExtractor()
    signal = np.sin(2 * np.pi * 440 * np.linspace(0, 1.0, 16000)).astype(np.float32)

    artifacts = extractor.extract_artifacts(signal, sample_rate=16000)

    assert isinstance(artifacts, GeneralizationArtifacts)
    assert 0.0 <= artifacts.phase_coherence_score <= 1.0
    assert 0.0 <= artifacts.pitch_jitter_score <= 1.0
    assert 0.0 <= artifacts.hf_vocoder_artifact_score <= 1.0
    assert 0.0 <= artifacts.generalization_risk_score <= 1.0


def test_generalization_extractor_short_signal():
    extractor = GeneralizationExtractor()
    short_signal = np.zeros(100, dtype=np.float32)

    artifacts = extractor.extract_artifacts(short_signal, sample_rate=16000)

    assert artifacts.generalization_risk_score == 0.0


def test_phase3_report_files_exist():
    reports = [
        "reports/phase3_generalization_status.json",
        "reports/phase3_generalization_report.md",
        "reports/PHASE3_FINAL_REPORT.md"
    ]

    for r in reports:
        assert os.path.exists(r), f"Missing Phase 3 report: {r}"
