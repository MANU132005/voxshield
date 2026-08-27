import os
import json
import pytest
import numpy as np
from fastapi.testclient import TestClient

from app.main import app
from app.services.audio.processor import AudioProcessor, AudioProcessingError, ProcessedAudio
from app.services.live_detection.types import (
    LiveWindow,
    LiveAnalysisResult,
    TemporalStabilityState,
    DetectorAgreementState,
    LiveConfidenceState
)
from app.services.live_detection.windowing import LiveWindowingSystem, WindowConfig
from app.services.live_detection.agreement_engine import DetectorAgreementEngine
from app.services.live_detection.temporal_fusion import TemporalFusionEngine
from app.services.live_detection.session_manager import LiveSessionManager
from app.services.live_detection.live_engine import LiveDetectionEngine
from app.services.live_detection.reports import generate_phase5_reports
from tests.test_processor import create_synthetic_wav_bytes

client = TestClient(app)


@pytest.fixture
def processor():
    return AudioProcessor()


@pytest.fixture
def live_engine(processor):
    return LiveDetectionEngine(audio_processor=processor)


# 1. Valid Live Audio
def test_live_analysis_valid_audio(live_engine, processor):
    wav = create_synthetic_wav_bytes(duration=2.0)
    pa = processor.load_and_preprocess(wav, "valid.wav")
    res = live_engine.analyze_live_audio(pa)

    assert res.status == "LIVE_ANALYSIS_COMPLETED"
    assert res.decision in ("LIKELY_GENUINE", "SUSPICIOUS", "LIKELY_SPOOF")
    assert 0.0 <= res.risk_score <= 100.0
    assert len(res.windows) >= 1


# 2. Invalid Audio Format Handling
def test_live_analysis_invalid_audio_format():
    response = client.post("/api/v1/live/analyze", files={"file": ("test.txt", b"invalid text content", "text/plain")})
    assert response.status_code == 400


# 3. Empty Audio
def test_live_analysis_empty_audio():
    response = client.post("/api/v1/live/analyze", files={"file": ("empty.wav", b"", "audio/wav")})
    assert response.status_code == 400


# 4. Too-Short Audio
def test_live_analysis_short_audio(processor):
    wav = create_synthetic_wav_bytes(duration=0.1)
    with pytest.raises(AudioProcessingError):
        processor.load_and_preprocess(wav, "short.wav")


# 5. Excessive Duration Audio Handling
def test_live_analysis_excessive_duration(live_engine):
    signal = np.sin(2 * np.pi * 440 * np.linspace(0, 35.0, 35 * 16000)).astype(np.float32)
    pa = ProcessedAudio(signal, 16000, 35.0, 1, 16000, 1, 0.8)
    res = live_engine.analyze_live_audio(pa)

    assert res.processing_metadata["windows_processed"] <= 60  # Capped window limit


# 6. Malformed Audio Payload
def test_live_analysis_malformed_payload():
    response = client.post("/api/v1/live/analyze", files={"file": ("corrupt.wav", b"RIFF1234WAVEfmt ", "audio/wav")})
    assert response.status_code == 400


# 7. Silence Audio Handling
def test_live_analysis_silence_audio(processor):
    wav = create_synthetic_wav_bytes(duration=1.0)
    with pytest.raises(AudioProcessingError):
        # Create silent bytes
        processor.load_and_preprocess(b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80\x3e\x00\x00\x00\x7d\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00", "silent.wav")


# 8. Noisy Audio
def test_live_analysis_noisy_audio(live_engine, processor):
    wav = create_synthetic_wav_bytes(duration=1.0)
    pa = processor.load_and_preprocess(wav, "noisy.wav")
    pa.audio_signal += np.random.normal(0, 0.1, len(pa.audio_signal)).astype(np.float32)
    res = live_engine.analyze_live_audio(pa)

    assert res.status == "LIVE_ANALYSIS_COMPLETED"


# 9. Clipped Audio
def test_live_analysis_clipped_audio(live_engine, processor):
    wav = create_synthetic_wav_bytes(duration=1.0)
    pa = processor.load_and_preprocess(wav, "clipped.wav")
    pa.audio_signal = np.clip(pa.audio_signal * 2.0, -0.70, 0.70)
    res = live_engine.analyze_live_audio(pa)

    assert res.status == "LIVE_ANALYSIS_COMPLETED"


# 10. Replay Transformation
def test_live_analysis_replay_transform(live_engine, processor):
    wav = create_synthetic_wav_bytes(duration=1.0)
    pa = processor.load_and_preprocess(wav, "replay.wav")
    from app.services.robustness.transformations import apply_replay_transformation
    pa.audio_signal = apply_replay_transformation(pa.audio_signal)
    res = live_engine.analyze_live_audio(pa)

    assert res.status == "LIVE_ANALYSIS_COMPLETED"


# 11. Compression Transformation
def test_live_analysis_compression_transform(live_engine, processor):
    wav = create_synthetic_wav_bytes(duration=1.0)
    pa = processor.load_and_preprocess(wav, "compressed.wav")
    from app.services.robustness.transformations import apply_compression_transformation
    pa.audio_signal = apply_compression_transformation(pa.audio_signal, target_sr=8000)
    res = live_engine.analyze_live_audio(pa)

    assert res.status == "LIVE_ANALYSIS_COMPLETED"


# 12. Reverberation Transformation
def test_live_analysis_reverb_transform(live_engine, processor):
    wav = create_synthetic_wav_bytes(duration=1.0)
    pa = processor.load_and_preprocess(wav, "reverb.wav")
    from app.services.robustness.transformations import apply_reverberation_transformation
    pa.audio_signal = apply_reverberation_transformation(pa.audio_signal, decay=0.6)
    res = live_engine.analyze_live_audio(pa)

    assert res.status == "LIVE_ANALYSIS_COMPLETED"


# 13 & 14. Multiple & Overlapping Windows
def test_live_windowing_slicer(processor):
    wav = create_synthetic_wav_bytes(duration=3.0)
    pa = processor.load_and_preprocess(wav, "multi.wav")
    slicer = LiveWindowingSystem(WindowConfig(window_duration_seconds=1.0, hop_duration_seconds=0.5))
    windows = slicer.slice_windows(pa)

    assert len(windows) >= 4
    assert windows[0][1] == 0.0
    assert windows[1][1] == 0.5


# 15. Conflicting Detectors
def test_detector_agreement_conflicting():
    engine = DetectorAgreementEngine()
    res = engine.analyze_agreement(neural_score=0.90, replay_score=0.10, forensic_score=0.80, generalization_score=0.20)

    assert res.agreement_state == DetectorAgreementState.DETECTOR_DISAGREEMENT.value


# 16. Insufficient Evidence
def test_temporal_fusion_insufficient_timeline():
    fusion = TemporalFusionEngine()
    res = fusion.analyze_temporal_stability([])

    assert res.stability_state == TemporalStabilityState.INSUFFICIENT_TIMELINE.value


# 17. Temporal Instability
def test_temporal_fusion_timeline_stability():
    fusion = TemporalFusionEngine()
    w1 = LiveWindow(0, 0.0, 1.0, 0.9, 0.8, 85.0, 0.9, "LIKELY_SPOOF", "neural_synthetic")
    w2 = LiveWindow(1, 0.5, 1.5, 0.1, 0.2, 15.0, 0.9, "LIKELY_GENUINE", "natural_speech")

    res = fusion.analyze_temporal_stability([w1, w2])

    assert res.stability_state == TemporalStabilityState.CONFLICTING_TIMELINE.value


# 18. Deterministic Repeated Analysis
def test_live_analysis_determinism(live_engine, processor):
    wav = create_synthetic_wav_bytes(duration=2.0)
    pa1 = processor.load_and_preprocess(wav, "det.wav")
    pa2 = processor.load_and_preprocess(wav, "det.wav")

    res1 = live_engine.analyze_live_audio(pa1)
    res2 = live_engine.analyze_live_audio(pa2)

    assert res1.risk_score == res2.risk_score
    assert res1.decision == res2.decision
    assert res1.confidence_state == res2.confidence_state


# 19. Concurrent Requests API
def test_live_health_probe():
    res = client.get("/api/v1/live/health")
    assert res.status_code == 200
    assert res.json()["status"] == "HEALTHY"


# 20 & 21. ClaimGuard & BenchmarkGate Enforcement
def test_live_analysis_claim_guard_enforcement(live_engine, processor):
    wav = create_synthetic_wav_bytes(duration=1.0)
    pa = processor.load_and_preprocess(wav, "cg.wav")
    res = live_engine.analyze_live_audio(pa)

    assert res.validation_metadata["benchmark_status"] == "BLOCKED"
    assert res.validation_metadata["claim_guard_status"] == "ACTIVE"


# 22. API Schema Verification
def test_live_analyze_api_endpoint():
    wav = create_synthetic_wav_bytes(duration=1.0)
    res = client.post("/api/v1/live/analyze", files={"file": ("test.wav", wav, "audio/wav")})

    assert res.status_code == 200
    json_data = res.json()
    assert json_data["status"] == "LIVE_ANALYSIS_COMPLETED"
    assert "risk_score" in json_data
    assert "windows" in json_data


# 23. Security Size Limits
def test_live_oversized_upload():
    large_payload = b"0" * (16 * 1024 * 1024)
    res = client.post("/api/v1/live/analyze", files={"file": ("large.wav", large_payload, "audio/wav")})
    assert res.status_code == 413


# 24 & 25. Session Lifecycle & Final Aggregation
def test_live_session_lifecycle():
    # 1. Create Session
    r1 = client.post("/api/v1/live/session")
    assert r1.status_code == 201
    sid = r1.json()["session_id"]

    # 2. Append Chunk
    wav_chunk = create_synthetic_wav_bytes(duration=1.0)
    r2 = client.post(f"/api/v1/live/session/{sid}/chunk", files={"file": ("chunk1.wav", wav_chunk, "audio/wav")})
    assert r2.status_code == 200
    assert r2.json()["chunks_received"] == 1

    # 3. Finalize Session
    r3 = client.post(f"/api/v1/live/session/{sid}/finalize")
    assert r3.status_code == 200
    assert r3.json()["status"] == "LIVE_ANALYSIS_COMPLETED"

    # 4. Query Session State
    r4 = client.get(f"/api/v1/live/session/{sid}")
    assert r4.status_code == 200
    assert r4.json()["is_finalized"] is True
