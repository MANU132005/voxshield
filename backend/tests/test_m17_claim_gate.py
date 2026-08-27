import pytest
from app.services.evaluation.claim_gate import ClaimGate


def test_claim_gate_blocks_real_benchmark_claims_when_missing_dataset():
    gate = ClaimGate(dataset_available=False, real_model_trained=False)
    claims = gate.evaluate_claims()

    assert claims["asvspoof_2019_accuracy"] == "BLOCKED"
    assert claims["asvspoof_2019_eer"] == "BLOCKED"
    assert claims["asvspoof_real_benchmark"] == "BLOCKED"
    assert claims["architecture_pipeline"] == "VERIFIED"


def test_claim_gate_verifies_claims_when_data_and_model_exist():
    gate = ClaimGate(dataset_available=True, real_model_trained=True)
    claims = gate.evaluate_claims()

    assert claims["architecture_pipeline"] == "VERIFIED"
    assert claims["latency_measurement"] == "MEASURED"
