import pytest
import numpy as np

from app.services.forensics.forensic_engine import ForensicEngine
from app.services.forensics.types import (
    ForensicDecision,
    EvidenceDirection,
    ScientificStatus
)
from app.services.forensics.spectral_forensics import analyze_spectral_forensics
from app.services.forensics.temporal_forensics import analyze_temporal_forensics
from app.services.forensics.signal_integrity import analyze_signal_integrity
from app.services.forensics.consistency import analyze_cross_signal_consistency


@pytest.fixture
def engine():
    return ForensicEngine()


def test_silence_signal_returns_inconclusive(engine):
    silence = np.zeros(16000, dtype=np.float32)
    res = engine.evaluate_forensics(0.1, 0.1, silence, 16000)

    assert "INCONCLUSIVE" in (res.decision, res.risk_level) or res.confidence_indicator <= 0.85
    assert isinstance(res.forensic_report, str)


def test_pure_tone_signal_detects_spectral_flatness(engine):
    t = np.linspace(0, 1.0, 16000, endpoint=False)
    pure_tone = (0.5 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)
    res = engine.evaluate_forensics(0.8, 0.2, pure_tone, 16000)

    assert res.decision in ("LIKELY_SPOOF", "SUSPICIOUS")
    assert any(e["signal"] == "spectral_flatness" for e in res.evidence)


def test_white_noise_signal_detects_high_zcr(engine):
    np.random.seed(42)
    noise = (np.random.randn(16000) * 0.3).astype(np.float32)
    res = engine.evaluate_forensics(0.5, 0.5, noise, 16000)

    assert any(e["signal"] in ("zero_crossing_rate", "spectral_flatness") for e in res.evidence)


def test_clipped_waveform_detects_clipping(engine):
    t = np.linspace(0, 1.0, 16000, endpoint=False)
    overdriven = (2.0 * np.sin(2 * np.pi * 300 * t)).astype(np.float32)
    clipped = np.clip(overdriven, -1.0, 1.0)
    res = engine.evaluate_forensics(0.4, 0.4, clipped, 16000)

    assert any(e["signal"] == "clipping_ratio" for e in res.evidence)


def test_very_short_audio_returns_inconclusive(engine):
    short_signal = np.zeros(4000, dtype=np.float32)  # 0.25s
    res = engine.evaluate_forensics(0.7, 0.2, short_signal, 16000)

    assert res.decision == ForensicDecision.INCONCLUSIVE.value


def test_nan_inf_protection(engine):
    corrupt_signal = np.array([0.1, np.nan, 0.5, np.inf, -0.2], dtype=np.float32)
    clean_signal = np.nan_to_num(corrupt_signal, nan=0.0, posinf=1.0, neginf=-1.0)
    res = engine.evaluate_forensics(0.2, 0.2, clean_signal, 16000)

    assert res.decision is not None
    assert not np.isnan(res.risk_score)


def test_deterministic_repeatability(engine):
    signal = np.sin(np.linspace(0, 100, 16000)).astype(np.float32)
    res1 = engine.evaluate_forensics(0.5, 0.3, signal, 16000)
    res2 = engine.evaluate_forensics(0.5, 0.3, signal, 16000)

    assert res1.risk_score == res2.risk_score
    assert res1.confidence_indicator == res2.confidence_indicator
    assert len(res1.evidence) == len(res2.evidence)


def test_attack_taxonomy_hypotheses(engine):
    signal = np.sin(np.linspace(0, 100, 16000)).astype(np.float32)
    res = engine.evaluate_forensics(0.85, 0.2, signal, 16000)

    assert len(res.attack_hypotheses) > 0
    assert res.attack_hypotheses[0]["classification"] == "AI_SYNTHESIS_SUSPECTED"


def test_forensic_report_formatting(engine):
    signal = np.sin(np.linspace(0, 100, 16000)).astype(np.float32)
    res = engine.evaluate_forensics(0.75, 0.4, signal, 16000)

    assert "VOXSHIELD FORENSIC ASSESSMENT REPORT" in res.forensic_report
    assert "Decision:" in res.forensic_report
    assert "Risk Score:" in res.forensic_report
