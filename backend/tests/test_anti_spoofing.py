import numpy as np
import pytest
from app.services.audio.processor import AudioProcessor
from app.services.audio.features import FeatureExtractor
from app.services.anti_spoofing.detector import AntiSpoofingDetector, AntiSpoofingResult
from app.services.anti_spoofing.model import VoiceAntiSpoofingResNet
from tests.test_processor import create_synthetic_wav_bytes


@pytest.fixture
def detector():
    return AntiSpoofingDetector(model_path="./models/anti_spoofing_resnet.pt")


@pytest.fixture
def processor():
    return AudioProcessor(target_sample_rate=16000, min_duration_seconds=0.5)


@pytest.fixture
def feature_extractor():
    return FeatureExtractor(sample_rate=16000)


def test_anti_spoofing_model_architecture():
    model = VoiceAntiSpoofingResNet()
    assert isinstance(model, VoiceAntiSpoofingResNet)


def test_anti_spoofing_detector_predict(detector, processor, feature_extractor):
    wav_bytes = create_synthetic_wav_bytes(sample_rate=16000, duration=1.0, channels=1)
    processed = processor.load_and_preprocess(wav_bytes, filename="test.wav")
    features = feature_extractor.extract_features(processed)

    result = detector.predict(features)

    assert isinstance(result, AntiSpoofingResult)
    assert 0.0 <= result.synthetic_score <= 1.0
    assert isinstance(result.is_synthetic, bool)
    assert 0.0 <= result.confidence <= 1.0
    assert result.model_version == "resnet18_logmel_v1.0"
    assert result.inference_time_ms >= 0.0


def test_anti_spoofing_detector_synthetic_score_helper(detector, processor, feature_extractor):
    wav_bytes = create_synthetic_wav_bytes(sample_rate=16000, duration=1.0, channels=1)
    processed = processor.load_and_preprocess(wav_bytes, filename="test.wav")
    features = feature_extractor.extract_features(processed)

    score = detector.predict_synthetic_score(features)

    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0


def test_anti_spoofing_detector_varying_temporal_frames(detector):
    # Test short frames (100 frames)
    short_log_mel = np.random.randn(80, 100).astype(np.float32)
    score_short = detector.predict_synthetic_score(short_log_mel)
    assert 0.0 <= score_short <= 1.0

    # Test long frames (500 frames)
    long_log_mel = np.random.randn(80, 500).astype(np.float32)
    score_long = detector.predict_synthetic_score(long_log_mel)
    assert 0.0 <= score_long <= 1.0
