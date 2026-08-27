from fastapi.testclient import TestClient
from app.main import app
import io

from tests.test_processor import create_synthetic_wav_bytes

client = TestClient(app)

def test_analyze_endpoint_mock_file():
    valid_wav_content = create_synthetic_wav_bytes(sample_rate=16000, duration=1.0, channels=1)
    files = {"file": ("test_sample.wav", io.BytesIO(valid_wav_content), "audio/wav")}

    response = client.post("/api/v1/analyze", files=files)
    assert response.status_code == 200
    
    data = response.json()
    assert "synthetic_score" in data
    assert "replay_score" in data
    assert "speaker_match" in data
    assert data["speaker_match"] is None
    assert "risk_score" in data
    assert "status" in data
    assert data["status"] in ["SAFE", "SUSPICIOUS", "HIGH_RISK"]
    assert "reasons" in data
    assert isinstance(data["reasons"], list)

def test_analyze_endpoint_empty_file():
    files = {"file": ("empty.wav", io.BytesIO(b""), "audio/wav")}
    response = client.post("/api/v1/analyze", files=files)
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()

def test_analyze_endpoint_unsupported_format():
    files = {"file": ("test.txt", io.BytesIO(b"some text content"), "text/plain")}
    response = client.post("/api/v1/analyze", files=files)
    assert response.status_code == 400
    assert "unsupported" in response.json()["detail"].lower()

def test_analyze_endpoint_short_audio():
    short_wav_content = create_synthetic_wav_bytes(sample_rate=16000, duration=0.2, channels=1)
    files = {"file": ("short.wav", io.BytesIO(short_wav_content), "audio/wav")}
    response = client.post("/api/v1/analyze", files=files)
    assert response.status_code == 400
    assert "too short" in response.json()["detail"].lower()

def test_analyze_endpoint_corrupted_audio():
    files = {"file": ("corrupt.wav", io.BytesIO(b"RIFF....BAD_HEADER_DATA"), "audio/wav")}
    response = client.post("/api/v1/analyze", files=files)
    assert response.status_code == 400
    assert "could not decode" in response.json()["detail"].lower() or "corrupted" in response.json()["detail"].lower()

