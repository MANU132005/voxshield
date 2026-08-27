import os
import json
import pytest
import numpy as np

from app.services.audio.processor import AudioProcessor, ProcessedAudio
from app.services.robustness.types import (
    RobustnessCondition,
    RobustnessConditionType,
    RobustnessResult,
    RobustnessAssessment
)
from app.services.robustness.transformations import (
    apply_replay_transformation,
    apply_noise_transformation,
    apply_reverberation_transformation,
    apply_compression_transformation,
    apply_clipping_transformation,
    apply_synthetic_variation_transformation,
    apply_controlled_perturbation_transformation
)
from app.services.robustness.runner import RobustnessRunner
from app.services.robustness.reports import generate_phase4_reports
from tests.test_processor import create_synthetic_wav_bytes


@pytest.fixture
def processed_audio():
    processor = AudioProcessor()
    wav_bytes = create_synthetic_wav_bytes(sample_rate=16000, duration=1.0, channels=1)
    return processor.load_and_preprocess(wav_bytes, "robustness_test.wav")


def test_transformations_reproducibility():
    signal = np.sin(2 * np.pi * 440 * np.linspace(0, 1.0, 16000)).astype(np.float32)

    replay = apply_replay_transformation(signal, severity="MEDIUM")
    noise1 = apply_noise_transformation(signal, snr_db=20.0, seed=42)
    noise2 = apply_noise_transformation(signal, snr_db=20.0, seed=42)
    reverb = apply_reverberation_transformation(signal, decay=0.5)
    codec = apply_compression_transformation(signal, target_sr=8000)
    clip = apply_clipping_transformation(signal, threshold=0.70)
    synth_var, status = apply_synthetic_variation_transformation(signal)
    pert = apply_controlled_perturbation_transformation(signal, pert_amp=0.02)

    assert len(replay) == len(signal)
    assert np.array_equal(noise1, noise2)
    assert len(reverb) == len(signal)
    assert len(codec) == len(signal)
    assert np.max(np.abs(clip)) <= 0.701
    assert status == "FIXTURE_APPLIED"
    assert len(pert) == len(signal)


def test_robustness_runner_evaluation(processed_audio):
    runner = RobustnessRunner()
    cond = RobustnessCondition(
        condition_id="RC_TEST",
        condition_type=RobustnessConditionType.NOISE.value,
        severity="LOW",
        parameters={"snr_db": 20.0},
        source_audio_id="TEST_01",
        description="Noise test"
    )

    res = runner.evaluate_condition(processed_audio, cond)

    assert isinstance(res, RobustnessResult)
    assert res.condition_id == "RC_TEST"
    assert res.baseline_latency_ms >= 0.0
    assert res.transformed_latency_ms >= 0.0
    assert res.transformation_latency_ms >= 0.0
    assert res.total_latency_ms > 0.0


def test_robustness_runner_standard_suite(processed_audio):
    runner = RobustnessRunner()
    assessment = runner.run_standard_suite(processed_audio)

    assert isinstance(assessment, RobustnessAssessment)
    assert assessment.overall_status == "ROBUSTNESS_ENGINE_VERIFIED"
    assert assessment.conditions_evaluated == 7
    assert 0.0 <= assessment.stability_ratio <= 1.0
    assert len(assessment.disclosures) == 2


def test_phase4_report_generation(processed_audio):
    runner = RobustnessRunner()
    assessment = runner.run_standard_suite(processed_audio)
    paths = generate_phase4_reports(assessment, output_dir="./reports")

    assert os.path.exists(paths["json_report"])
    assert os.path.exists(paths["md_report"])
    assert os.path.exists(paths["final_report"])

    with open(paths["json_report"], "r", encoding="utf-8") as f:
        data = json.load(f)
        assert data["overall_status"] == "ROBUSTNESS_ENGINE_VERIFIED"
        assert len(data["results"]) == 7
