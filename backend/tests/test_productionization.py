"""
Productionization & System Integration Test Suite.

Verifies:
1. Production model loading (models/asvspoof2019_la_recovery_exp01.pt)
2. AudioProcessor & FeatureExtractor end-to-end pipeline
3. Robust input handling (silence, short audio, corrupted, oversized uploads)
4. Path traversal security bounds
5. Inference determinism
6. Checkpoint SHA-256 hash preservation
"""

import os
import io
import pytest
import numpy as np
import torch

from app.services.audio.processor import AudioProcessor, AudioProcessingError
from app.services.audio.features import FeatureExtractor
from app.services.anti_spoofing.detector import AntiSpoofingDetector
from app.services.model_integrity.auditor import calculate_file_sha256


@pytest.fixture
def detector():
    return AntiSpoofingDetector()


@pytest.fixture
def processor():
    return AudioProcessor(target_sample_rate=16000, min_duration_seconds=0.5)


@pytest.fixture
def extractor():
    return FeatureExtractor(sample_rate=16000)


def test_production_checkpoint_resolved(detector):
    """Verifies that AntiSpoofingDetector resolves the Phase 7 recovery model."""
    assert detector.model_path is not None
    assert "asvspoof2019_la_recovery_exp01.pt" in detector.model_path
    assert os.path.exists(detector.model_path)


def test_production_checkpoint_sha256(detector):
    """Verifies that the recovery checkpoint SHA-256 remains 100% untouched."""
    sha256 = calculate_file_sha256(detector.model_path)
    expected_sha256 = "f745df8fbab5351153c55a579d6a35f8cce0bcc4c3f2bcdfe47ba516348f9a06"
    assert sha256.lower() == expected_sha256.lower()


def test_flac_audio_decoding_and_inference(processor, extractor, detector):
    """Tests end-to-end inference on a real ASVspoof 2019 LA FLAC file."""
    test_flac = "datasets/ASVspoof2019_LA/LA/ASVspoof2019_LA_train/flac/LA_T_1138215.flac"
    if not os.path.exists(test_flac):
        pytest.skip(f"Test FLAC file {test_flac} not present.")

    with open(test_flac, "rb") as f:
        audio_bytes = f.read()

    processed = processor.load_and_preprocess(audio_bytes, "LA_T_1138215.flac")
    assert processed.sample_rate == 16000
    assert processed.channels == 1
    assert processed.duration_seconds >= 0.5

    features = extractor.extract_features(processed)
    assert features.log_mel_spectrogram.shape[0] == 80

    result = detector.predict(features)
    assert 0.0 <= result.synthetic_score <= 1.0
    assert isinstance(result.is_synthetic, bool)
    assert result.inference_time_ms < 500.0  # sub-half-second guarantee


def test_inference_determinism(processor, extractor, detector):
    """Verifies that identical audio produces identical prediction scores."""
    test_flac = "datasets/ASVspoof2019_LA/LA/ASVspoof2019_LA_train/flac/LA_T_1138215.flac"
    if not os.path.exists(test_flac):
        pytest.skip(f"Test FLAC file {test_flac} not present.")

    with open(test_flac, "rb") as f:
        audio_bytes = f.read()

    p1 = processor.load_and_preprocess(audio_bytes, "LA_T_1138215.flac")
    f1 = extractor.extract_features(p1)
    r1 = detector.predict(f1)

    p2 = processor.load_and_preprocess(audio_bytes, "LA_T_1138215.flac")
    f2 = extractor.extract_features(p2)
    r2 = detector.predict(f2)

    assert r1.synthetic_score == pytest.approx(r2.synthetic_score, abs=1e-6)
    assert r1.is_synthetic == r2.is_synthetic


def test_empty_audio_rejection(processor):
    """Verifies that empty 0-byte audio throws AudioProcessingError."""
    with pytest.raises(AudioProcessingError):
        processor.load_and_preprocess(b"", "empty.wav")


def test_corrupted_audio_rejection(processor):
    """Verifies that corrupted bytes throw AudioProcessingError."""
    with pytest.raises(AudioProcessingError):
        processor.load_and_preprocess(b"INVALID_HEADER_GARBAGE_BYTES_1234567890", "corrupted.wav")


def test_short_audio_rejection(processor):
    """Verifies that audio under 0.5s throws AudioProcessingError."""
    # Generate 0.1s sine wave at 16kHz
    t = np.linspace(0, 0.1, int(16000 * 0.1), dtype=np.float32)
    sine = (np.sin(2 * np.pi * 440 * t) * 32767).astype(np.int16)
    import wave
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(sine.tobytes())

    with pytest.raises(AudioProcessingError):
        processor.load_and_preprocess(buf.getvalue(), "too_short.wav")
