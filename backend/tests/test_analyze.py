from fastapi.testclient import TestClient
from app.main import app
import io

client = TestClient(app)

def test_analyze_endpoint_mock_file():
    fake_audio_content = b"RIFF....WAVEfmt ....data...."
    files = {"file": ("test_sample.wav", io.BytesIO(fake_audio_content), "audio/wav")}

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

