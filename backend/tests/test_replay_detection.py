import math
import numpy as np
import pytest

from app.services.audio.processor import AudioProcessor
from app.services.replay_detection.dsp import ReplayDetector, ReplayFeatures, ReplayDetectionResult
from tests.test_processor import create_synthetic_wav_bytes


@pytest.fixture
def replay_detector():
    return ReplayDetector(sample_rate=16000)


@pytest.fixture
def processor():
    return AudioProcessor(target_sample_rate=16000, min_duration_seconds=0.5)


def test_valid_audio_produces_replay_result(replay_detector, processor):
    wav_bytes = create_synthetic_wav_bytes(sample_rate=16000, duration=1.0, channels=1)
    processed = processor.load_and_preprocess(wav_bytes, filename="test.wav")

    result = replay_detector.analyze_replay_detailed(processed)

    assert isinstance(result, ReplayDetectionResult)
    assert 0.0 <= result.replay_score <= 1.0
    assert 0.0 <= result.confidence <= 1.0
    assert result.risk_level in ("LOW", "MEDIUM", "HIGH")
    assert isinstance(result.triggered_indicators, list)
    assert isinstance(result.feature_summary, dict)
    assert result.processing_time_ms >= 0.0
    assert result.detector_version == "dsp_replay_v1.0"


def test_silence_handled_safely(replay_detector):
    silent_signal = np.zeros(16000, dtype=np.float32)
    feats = replay_detector.extract_replay_features(silent_signal)

    assert isinstance(feats, ReplayFeatures)
    assert feats.rms_energy >= 0.0
    assert feats.peak_amplitude == 0.0
    assert feats.clipping_ratio == 0.0
    assert not math.isnan(feats.spectral_centroid_hz)
    assert not math.isnan(feats.spectral_rolloff_hz)
    assert not math.isinf(feats.spectral_centroid_hz)


def test_constant_sine_wave_deterministic_features(replay_detector):
    t = np.linspace(0, 1.0, 16000, endpoint=False)
    sine_signal = (0.5 * np.sin(2 * np.pi * 440.0 * t)).astype(np.float32)

    feats1 = replay_detector.extract_replay_features(sine_signal)
    feats2 = replay_detector.extract_replay_features(sine_signal)

    assert feats1.spectral_centroid_hz == feats2.spectral_centroid_hz
    assert feats1.rms_energy == feats2.rms_energy
    assert feats1.peak_amplitude == feats2.peak_amplitude


def test_broadband_noise_finite_features(replay_detector):
    np.random.seed(42)
    noise_signal = (0.2 * np.random.randn(16000)).astype(np.float32)

    feats = replay_detector.extract_replay_features(noise_signal)

    assert not math.isnan(feats.spectral_centroid_hz)
    assert not math.isnan(feats.spectral_rolloff_hz)
    assert not math.isnan(feats.high_freq_energy_ratio)
    assert 0.0 <= feats.high_freq_energy_ratio <= 1.0


def test_spectral_flux_reacts_to_changing_signal(replay_detector):
    t = np.linspace(0, 1.0, 16000, endpoint=False)
    # Static tone
    static_tone = (0.5 * np.sin(2 * np.pi * 440.0 * t)).astype(np.float32)
    # Frequency chirp changing from 100Hz to 4000Hz
    chirp_freq = np.linspace(100.0, 4000.0, 16000)
    chirp = (0.5 * np.sin(2 * np.pi * chirp_freq * t)).astype(np.float32)

    feats_static = replay_detector.extract_replay_features(static_tone)
    feats_chirp = replay_detector.extract_replay_features(chirp)

    assert feats_chirp.spectral_flux_mean > feats_static.spectral_flux_mean


def test_spectral_centroid_low_vs_high_frequency(replay_detector):
    t = np.linspace(0, 1.0, 16000, endpoint=False)
    low_tone = (0.5 * np.sin(2 * np.pi * 200.0 * t)).astype(np.float32)
    high_tone = (0.5 * np.sin(2 * np.pi * 5000.0 * t)).astype(np.float32)

    feats_low = replay_detector.extract_replay_features(low_tone)
    feats_high = replay_detector.extract_replay_features(high_tone)

    assert feats_high.spectral_centroid_hz > feats_low.spectral_centroid_hz


def test_spectral_rolloff_bounds(replay_detector):
    t = np.linspace(0, 1.0, 16000, endpoint=False)
    tone = (0.5 * np.sin(2 * np.pi * 1000.0 * t)).astype(np.float32)

    feats = replay_detector.extract_replay_features(tone)

    assert 0.0 <= feats.spectral_rolloff_hz <= 8000.0


def test_spectral_bandwidth_non_negative(replay_detector):
    t = np.linspace(0, 1.0, 16000, endpoint=False)
    tone = (0.5 * np.sin(2 * np.pi * 1000.0 * t)).astype(np.float32)

    feats = replay_detector.extract_replay_features(tone)

    assert feats.spectral_bandwidth_hz >= 0.0


def test_high_freq_energy_ratio_bounded(replay_detector):
    t = np.linspace(0, 1.0, 16000, endpoint=False)
    high_tone = (0.5 * np.sin(2 * np.pi * 7000.0 * t)).astype(np.float32)

    feats = replay_detector.extract_replay_features(high_tone)

    assert 0.0 <= feats.high_freq_energy_ratio <= 1.0
    assert feats.high_freq_energy_ratio > 0.1


def test_rms_energy_non_negative(replay_detector):
    t = np.linspace(0, 1.0, 16000, endpoint=False)
    tone = (0.5 * np.sin(2 * np.pi * 440.0 * t)).astype(np.float32)

    feats = replay_detector.extract_replay_features(tone)

    assert feats.rms_energy > 0.0


def test_peak_amplitude_bounded(replay_detector):
    t = np.linspace(0, 1.0, 16000, endpoint=False)
    tone = (0.8 * np.sin(2 * np.pi * 440.0 * t)).astype(np.float32)

    feats = replay_detector.extract_replay_features(tone)

    assert abs(feats.peak_amplitude - 0.8) < 1e-4


def test_clipping_detection(replay_detector):
    # Signal with 10% clipped samples at 1.0
    signal = (0.5 * np.sin(np.linspace(0, 100, 16000))).astype(np.float32)
    signal[:1600] = 1.0  # Force clipping

    feats = replay_detector.extract_replay_features(signal)

    assert feats.clipping_ratio >= 0.09


def test_zero_crossing_rate_bounded(replay_detector):
    t = np.linspace(0, 1.0, 16000, endpoint=False)
    tone = (0.5 * np.sin(2 * np.pi * 1000.0 * t)).astype(np.float32)

    feats = replay_detector.extract_replay_features(tone)

    assert 0.0 <= feats.zero_crossing_rate <= 1.0


def test_transient_detection_deterministic(replay_detector):
    t = np.linspace(0, 1.0, 16000, endpoint=False)
    signal = (0.05 * np.sin(2 * np.pi * 440.0 * t)).astype(np.float32)
    # Add pop spikes
    signal[4000:4050] = 0.9
    signal[8000:8050] = 0.9

    feats = replay_detector.extract_replay_features(signal)

    assert feats.transient_density > 0.0


def test_replay_score_deterministic(replay_detector):
    t = np.linspace(0, 1.0, 16000, endpoint=False)
    signal = (0.5 * np.sin(2 * np.pi * 440.0 * t)).astype(np.float32)

    score1 = replay_detector.analyze_replay(signal)
    score2 = replay_detector.analyze_replay(signal)

    assert score1 == score2


def test_replay_score_bounded(replay_detector):
    t = np.linspace(0, 1.0, 16000, endpoint=False)
    signal = (0.5 * np.sin(2 * np.pi * 440.0 * t)).astype(np.float32)

    score = replay_detector.analyze_replay(signal)

    assert 0.0 <= score <= 1.0


def test_no_nan_inf_in_features(replay_detector):
    np.random.seed(42)
    test_signals = [
        np.zeros(16000, dtype=np.float32),
        np.ones(16000, dtype=np.float32),
        np.random.randn(16000).astype(np.float32),
        np.array([1.0, -1.0] * 8000, dtype=np.float32)
    ]

    for sig in test_signals:
        feats = replay_detector.extract_replay_features(sig)
        for field_name, val in feats.__dict__.items():
            assert not math.isnan(val), f"NaN found in {field_name}"
            assert not math.isinf(val), f"Inf found in {field_name}"


def test_invalid_input_type_handled_safely(replay_detector):
    score = replay_detector.analyze_replay(None)
    assert 0.0 <= score <= 1.0


def test_processing_time_recorded(replay_detector):
    t = np.linspace(0, 1.0, 16000, endpoint=False)
    signal = (0.5 * np.sin(2 * np.pi * 440.0 * t)).astype(np.float32)

    res = replay_detector.analyze_replay_detailed(signal)

    assert res.processing_time_ms >= 0.0


def test_reasons_populated_on_clipping(replay_detector):
    signal = np.ones(16000, dtype=np.float32)  # 100% clipped

    res = replay_detector.analyze_replay_detailed(signal)

    assert len(res.triggered_indicators) > 0
    assert any("clipping" in reason.lower() for reason in res.triggered_indicators)
