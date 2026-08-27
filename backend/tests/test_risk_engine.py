import pytest
import numpy as np
from fastapi.testclient import TestClient

from app.main import app
from app.services.risk_engine.evaluator import (
    RiskEvaluator,
    RiskEngine,
    RiskAssessment,
    RiskLevel,
    Verdict,
    _sanitize_float
)
from app.services.anti_spoofing.detector import AntiSpoofingResult
from app.services.replay_detection.dsp import ReplayDetectionResult
from app.services.audio.processor import ProcessedAudio
from tests.test_processor import create_synthetic_wav_bytes


@pytest.fixture
def evaluator():
    return RiskEvaluator()


@pytest.fixture
def client():
    return TestClient(app)


def test_genuine_low_risk_signal(evaluator):
    res = evaluator.evaluate_risk(synthetic_input=0.10, replay_input=0.10)

    assert res.verdict == Verdict.AUTHENTIC.value
    assert res.risk_level == RiskLevel.LOW.value
    assert res.risk_score < 30.0
    assert 0.0 <= res.confidence <= 1.0


def test_strong_synthetic_signal(evaluator):
    res = evaluator.evaluate_risk(synthetic_input=0.85, replay_input=0.10)

    assert res.verdict == Verdict.SPOOF_SUSPECTED.value
    assert res.risk_level in (RiskLevel.HIGH.value, RiskLevel.CRITICAL.value)
    assert "synthetic_voice" in res.attack_indicators
    assert any(e["code"] == "SYNTHETIC_VOICE_HIGH" for e in res.evidence)


def test_strong_replay_signal(evaluator):
    res = evaluator.evaluate_risk(synthetic_input=0.10, replay_input=0.80)

    assert res.verdict == Verdict.REPLAY_SUSPECTED.value
    assert res.risk_level == RiskLevel.HIGH.value
    assert "replay_attack" in res.attack_indicators
    assert any(e["code"] == "REPLAY_ATTACK_HIGH" for e in res.evidence)


def test_strong_synthetic_and_replay_critical(evaluator):
    res = evaluator.evaluate_risk(synthetic_input=0.90, replay_input=0.85)

    assert res.verdict == Verdict.HIGH_RISK.value
    assert res.risk_level == RiskLevel.CRITICAL.value
    assert res.risk_score >= 75.0
    assert any(e["code"] == "COMBINED_MULTI_THREAT" for e in res.evidence)


def test_weak_synthetic_and_weak_replay_suspicious(evaluator):
    res = evaluator.evaluate_risk(synthetic_input=0.45, replay_input=0.45)

    assert res.verdict == Verdict.SUSPICIOUS.value
    assert res.risk_level == RiskLevel.MEDIUM.value
    assert 30.0 <= res.risk_score < 55.0


def test_missing_synthetic_detector_output(evaluator):
    res = evaluator.evaluate_risk(synthetic_input=None, replay_input=0.20)

    assert isinstance(res, RiskAssessment)
    assert 0.0 <= res.risk_score <= 100.0


def test_missing_replay_detector_output(evaluator):
    res = evaluator.evaluate_risk(synthetic_input=0.20, replay_input=None)

    assert isinstance(res, RiskAssessment)
    assert 0.0 <= res.risk_score <= 100.0


def test_poor_audio_quality_clipping(evaluator):
    # ProcessedAudio with clipped samples
    sig = np.ones(16000, dtype=np.float32)
    audio = ProcessedAudio(
        audio_signal=sig,
        sample_rate=16000,
        duration_seconds=1.0,
        channels=1,
        original_sample_rate=16000,
        original_channels=1,
        peak_amplitude=1.0
    )

    res = evaluator.evaluate_risk(synthetic_input=0.10, replay_input=0.10, processed_audio=audio)

    assert "signal_anomaly" in res.attack_indicators
    assert any(e["code"] == "SIGNAL_CLIPPING_SATURATION" for e in res.evidence)


def test_nan_input_handling(evaluator):
    res = evaluator.evaluate_risk(synthetic_input=float("nan"), replay_input=float("nan"))

    assert not np.isnan(res.risk_score)
    assert 0.0 <= res.risk_score <= 100.0


def test_infinity_input_handling(evaluator):
    res = evaluator.evaluate_risk(synthetic_input=float("inf"), replay_input=float("-inf"))

    assert not np.isinf(res.risk_score)
    assert 0.0 <= res.risk_score <= 100.0


def test_negative_score_input_handling(evaluator):
    res = evaluator.evaluate_risk(synthetic_input=-0.5, replay_input=-10.0)

    assert res.risk_score >= 0.0


def test_score_greater_than_one_clamping(evaluator):
    res = evaluator.evaluate_risk(synthetic_input=5.0, replay_input=99.0)

    assert res.risk_score <= 100.0


def test_conflicting_signals(evaluator):
    # High synthetic, low replay
    res1 = evaluator.evaluate_risk(synthetic_input=0.95, replay_input=0.05)
    # Low synthetic, high replay
    res2 = evaluator.evaluate_risk(synthetic_input=0.05, replay_input=0.95)

    assert res1.verdict == Verdict.SPOOF_SUSPECTED.value
    assert res2.verdict == Verdict.REPLAY_SUSPECTED.value


def test_deterministic_repeated_evaluation(evaluator):
    res1 = evaluator.evaluate_risk(synthetic_input=0.62, replay_input=0.41)
    res2 = evaluator.evaluate_risk(synthetic_input=0.62, replay_input=0.41)

    assert res1.risk_score == res2.risk_score
    assert res1.verdict == res2.verdict
    assert res1.confidence == res2.confidence


def test_boundary_thresholds(evaluator):
    res_low = evaluator.evaluate_risk(synthetic_input=0.0, replay_input=0.0)
    res_high = evaluator.evaluate_risk(synthetic_input=1.0, replay_input=1.0)

    assert res_low.risk_score == 0.0 or res_low.risk_score < 10.0
    assert res_high.risk_score == 100.0


def test_evidence_generation_structure(evaluator):
    res = evaluator.evaluate_risk(synthetic_input=0.88, replay_input=0.75)

    assert isinstance(res.evidence, list)
    assert len(res.evidence) >= 2
    for item in res.evidence:
        assert "code" in item
        assert "category" in item
        assert "severity" in item
        assert "observed_value" in item
        assert "threshold" in item
        assert "message" in item


def test_verdict_correctness(evaluator):
    res = evaluator.evaluate_risk(synthetic_input=0.10, replay_input=0.10)
    assert res.verdict == Verdict.AUTHENTIC.value

    res_crit = evaluator.evaluate_risk(synthetic_input=0.95, replay_input=0.95)
    assert res_crit.verdict == Verdict.HIGH_RISK.value


def test_risk_score_always_in_zero_to_hundred_range(evaluator):
    test_cases = [
        (0.0, 0.0), (1.0, 1.0), (-1.0, 2.0), (float("nan"), 0.5), (0.5, float("inf"))
    ]
    for s_in, r_in in test_cases:
        res = evaluator.evaluate_risk(synthetic_input=s_in, replay_input=r_in)
        assert 0.0 <= res.risk_score <= 100.0


def test_confidence_always_in_zero_to_one_range(evaluator):
    res = evaluator.evaluate_risk(synthetic_input=0.5, replay_input=0.5)
    assert 0.0 <= res.confidence <= 1.0


def test_malformed_input_cannot_crash_evaluator(evaluator):
    malformed_inputs = [
        ("string_input", {}),
        ([], None),
        ({"bad": "dict"}, "invalid"),
    ]
    for m_synth, m_replay in malformed_inputs:
        res = evaluator.evaluate_risk(synthetic_input=m_synth, replay_input=m_replay)
        assert isinstance(res, RiskAssessment)
        assert 0.0 <= res.risk_score <= 100.0


def test_legacy_risk_engine_backward_compatibility():
    legacy_engine = RiskEngine()
    result = legacy_engine.evaluate(synthetic_score=0.80, replay_score=0.50)

    assert "synthetic_score" in result
    assert "replay_score" in result
    assert "speaker_match" in result
    assert "risk_score" in result
    assert "status" in result
    assert "reasons" in result
    assert 0.0 <= result["risk_score"] <= 1.0


def test_analyze_endpoint_integration_m11(client):
    wav_bytes = create_synthetic_wav_bytes(sample_rate=16000, duration=1.0, channels=1)

    response = client.post(
        "/api/v1/analyze",
        files={"file": ("test_m11.wav", wav_bytes, "audio/wav")}
    )

    assert response.status_code == 200
    data = response.json()
    assert "synthetic_score" in data
    assert "replay_score" in data
    assert "risk_score" in data
    assert "status" in data
    assert "reasons" in data
    assert "risk_level" in data
    assert "verdict" in data
    assert "confidence" in data
    assert "evaluator_version" in data
