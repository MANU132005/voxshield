import math
import numpy as np
import pytest
from app.services.audio.processor import AudioProcessor, AudioProcessingError
from app.services.audio.features import LogMelExtractor, LFCCExtractor, FeatureExtractor, ExtractedFeatures
from tests.test_processor import create_synthetic_wav_bytes


@pytest.fixture
def processor():
    return AudioProcessor(target_sample_rate=16000, min_duration_seconds=0.5)


@pytest.fixture
def feature_extractor():
    return FeatureExtractor(sample_rate=16000)


def test_log_mel_extraction_dimensions_and_dtype(processor):
    wav_bytes = create_synthetic_wav_bytes(sample_rate=16000, duration=1.0, channels=1)
    processed = processor.load_and_preprocess(wav_bytes, filename="test.wav")

    log_mel_extractor = LogMelExtractor(sample_rate=16000, n_mels=80)
    log_mel = log_mel_extractor.extract(processed.audio_signal)

    assert isinstance(log_mel, np.ndarray)
    assert log_mel.dtype == np.float32
    assert log_mel.ndim == 2
    assert log_mel.shape[0] == 80
    assert log_mel.shape[1] > 0


def test_lfcc_extraction_dimensions_and_dtype(processor):
    wav_bytes = create_synthetic_wav_bytes(sample_rate=16000, duration=1.0, channels=1)
    processed = processor.load_and_preprocess(wav_bytes, filename="test.wav")

    lfcc_extractor = LFCCExtractor(sample_rate=16000, n_filters=60, n_lfcc=20)
    lfcc = lfcc_extractor.extract(processed.audio_signal)

    assert isinstance(lfcc, np.ndarray)
    assert lfcc.dtype == np.float32
    assert lfcc.ndim == 2
    assert lfcc.shape[0] == 20
    assert lfcc.shape[1] > 0


def test_unified_feature_extractor_coordinator(processor, feature_extractor):
    wav_bytes = create_synthetic_wav_bytes(sample_rate=16000, duration=1.5, channels=1)
    processed = processor.load_and_preprocess(wav_bytes, filename="test.wav")

    features = feature_extractor.extract_features(processed)

    assert isinstance(features, ExtractedFeatures)
    assert features.sample_rate == 16000
    assert features.log_mel_spectrogram.shape[0] == 80
    assert features.lfcc.shape[0] == 20
    assert features.log_mel_spectrogram.shape[1] == features.n_frames
    assert features.lfcc.shape[1] == features.n_frames
    assert "n_mels" in features.parameters
    assert features.parameters["n_mels"] == 80
    assert features.parameters["n_lfcc"] == 20


def test_all_extracted_features_are_finite(processor, feature_extractor):
    wav_bytes = create_synthetic_wav_bytes(sample_rate=16000, duration=1.0, channels=1)
    processed = processor.load_and_preprocess(wav_bytes, filename="test.wav")

    features = feature_extractor.extract_features(processed)

    assert np.all(np.isfinite(features.log_mel_spectrogram)), "Log-Mel contains non-finite values (NaN/Inf)"
    assert np.all(np.isfinite(features.lfcc)), "LFCC contains non-finite values (NaN/Inf)"


def test_deterministic_repeatability(processor, feature_extractor):
    wav_bytes = create_synthetic_wav_bytes(sample_rate=16000, duration=1.0, channels=1)
    processed1 = processor.load_and_preprocess(wav_bytes, filename="test.wav")
    processed2 = processor.load_and_preprocess(wav_bytes, filename="test.wav")

    features1 = feature_extractor.extract_features(processed1)
    features2 = feature_extractor.extract_features(processed2)

    assert features1.log_mel_spectrogram.shape == features2.log_mel_spectrogram.shape
    assert features1.lfcc.shape == features2.lfcc.shape
    assert np.array_equal(features1.log_mel_spectrogram, features2.log_mel_spectrogram)
    assert np.array_equal(features1.lfcc, features2.lfcc)


def test_varying_audio_durations(processor, feature_extractor):
    durations = [0.5, 1.0, 2.5]
    frame_counts = []

    for dur in durations:
        wav_bytes = create_synthetic_wav_bytes(sample_rate=16000, duration=dur, channels=1)
        processed = processor.load_and_preprocess(wav_bytes, filename=f"test_{dur}s.wav")
        features = feature_extractor.extract_features(processed)

        assert features.log_mel_spectrogram.shape[0] == 80
        assert features.lfcc.shape[0] == 20
        frame_counts.append(features.n_frames)

    # Frame counts should strictly increase with longer duration
    assert frame_counts[0] < frame_counts[1] < frame_counts[2]


def test_invalid_audio_rejected_before_extraction(processor, feature_extractor):
    # Silent audio is rejected during preprocessing with AudioProcessingError
    silent_bytes = create_synthetic_wav_bytes(sample_rate=16000, duration=1.0, channels=1, amplitude=0.0)
    with pytest.raises(AudioProcessingError):
        processed = processor.load_and_preprocess(silent_bytes, filename="silent.wav")
        feature_extractor.extract_features(processed)
