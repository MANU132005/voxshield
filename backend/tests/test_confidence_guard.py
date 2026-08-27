import pytest
from app.services.forensics.uncertainty import evaluate_uncertainty
from app.services.forensics.types import EvidenceItem, EvidenceDirection, ScientificStatus


def test_short_audio_duration_penalty():
    conf_ind, basis = evaluate_uncertainty(0.4, [], "REAL_ASVSPOOF_TRAINED")

    assert conf_ind <= 0.70
    assert any("Short audio duration" in b for b in basis)


def test_demo_model_provenance_penalty():
    conf_ind, basis = evaluate_uncertainty(1.5, [], "DEMO_DSP_SYNTHETIC_DATASET")

    assert conf_ind <= 0.80
    assert any("trained on DSP demo signals" in b for b in basis)


def test_unanimous_spoof_evidence_bonus():
    ev = [
        EvidenceItem("EV1", "SPECTRAL", "flatness", 0.1, 0.8, EvidenceDirection.SUPPORTS_SPOOF.value, 0.9, ScientificStatus.INFERRED.value, "Flat")
    ]
    conf_ind, basis = evaluate_uncertainty(1.5, ev, "REAL_ASVSPOOF_TRAINED")

    assert conf_ind >= 0.85
    assert any("consistently support spoof" in b for b in basis)


test_contradictory_evidence_penalty_data = [
    EvidenceItem("EV1", "SPECTRAL", "flatness", 0.1, 0.8, EvidenceDirection.SUPPORTS_SPOOF.value, 0.9, ScientificStatus.INFERRED.value, "Flat"),
    EvidenceItem("EV2", "INTEGRITY", "clean", 0.9, 0.8, EvidenceDirection.SUPPORTS_GENUINE.value, 0.9, ScientificStatus.INFERRED.value, "Clean")
]


def test_contradictory_evidence_penalty():
    conf_ind, basis = evaluate_uncertainty(1.5, test_contradictory_evidence_penalty_data, "REAL_ASVSPOOF_TRAINED")

    assert conf_ind <= 0.80
    assert any("Conflicting evidence" in b for b in basis)
