import pytest
import numpy as np

from app.services.adversarial.perturbation_engine import PerturbationEngine
from app.services.adversarial.adversarial_runner import AdversarialRunner
from app.services.adversarial.types import PerturbationType, PerturbationCase


@pytest.fixture
def runner():
    return AdversarialRunner()


def test_gaussian_noise_generator():
    signal = np.zeros(16000, dtype=np.float32)
    p_engine = PerturbationEngine()
    case = PerturbationCase("T1", PerturbationType.GAUSSIAN_NOISE.value, {"snr_db": 20.0}, "Noise test")
    out = p_engine.perturb_signal(signal, case)

    assert len(out) == len(signal)
    assert not np.array_equal(out, signal)
    assert np.max(np.abs(out)) <= 1.0


def test_hard_clipping_generator():
    signal = np.sin(np.linspace(0, 100, 16000)).astype(np.float32) * 1.5
    p_engine = PerturbationEngine()
    case = PerturbationCase("T2", PerturbationType.HARD_CLIPPING.value, {"threshold": 0.8}, "Clip test")
    out = p_engine.perturb_signal(signal, case)

    assert np.max(np.abs(out)) <= 0.801


def test_gain_attenuation_generator():
    signal = np.ones(1000, dtype=np.float32)
    p_engine = PerturbationEngine()
    case = PerturbationCase("T3", PerturbationType.GAIN_ATTENUATION.value, {"factor": 0.5}, "Gain test")
    out = p_engine.perturb_signal(signal, case)

    assert np.allclose(out, 0.5)


def test_resampling_generator():
    signal = np.sin(np.linspace(0, 100, 16000)).astype(np.float32)
    p_engine = PerturbationEngine()
    case = PerturbationCase("T4", PerturbationType.RESAMPLING_DOWN_UP.value, {"target_sr": 8000}, "Resample test")
    out = p_engine.perturb_signal(signal, case)

    assert len(out) == len(signal)


def test_high_freq_noise_generator():
    signal = np.zeros(16000, dtype=np.float32)
    p_engine = PerturbationEngine()
    case = PerturbationCase("T5", PerturbationType.HIGH_FREQ_NOISE.value, {"noise_amp": 0.1}, "HF test")
    out = p_engine.perturb_signal(signal, case)

    assert np.max(np.abs(out)) <= 0.101


def test_pop_transient_generator():
    signal = np.zeros(16000, dtype=np.float32)
    p_engine = PerturbationEngine()
    case = PerturbationCase("T6", PerturbationType.POP_TRANSIENT_INSERTION.value, {"location": 0.5, "pop_amp": 0.95}, "Pop test")
    out = p_engine.perturb_signal(signal, case)

    assert out[8000] == 0.95


def test_adversarial_suite_execution(runner):
    signal = np.sin(np.linspace(0, 100, 16000)).astype(np.float32)
    results = runner.run_adversarial_suite(signal)

    assert len(results) >= 5
    for r in results:
        assert "case_id" in r
        assert "observed_effect" in r
        assert r["claim_status"] == "INFERRED"


def test_invalid_attack_type_fallback():
    signal = np.zeros(1000, dtype=np.float32)
    p_engine = PerturbationEngine()
    case = PerturbationCase("T7", "INVALID_ATTACK_TYPE", {}, "Fallback test")
    out = p_engine.perturb_signal(signal, case)

    assert len(out) == len(signal)
