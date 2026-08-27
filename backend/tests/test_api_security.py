import pytest
import numpy as np
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from tests.test_processor import create_synthetic_wav_bytes


@pytest.fixture
def client():
    return TestClient(app)


def test_empty_upload_rejected(client):
    response = client.post(
        "/api/v1/analyze",
        files={"file": ("empty.wav", b"", "audio/wav")}
    )
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "BAD_REQUEST"
    assert "X-Request-ID" in response.headers


def test_oversized_upload_rejected(client):
    # Create binary payload > 15 MB
    oversized_bytes = b"0" * (16 * 1024 * 1024)
    response = client.post(
        "/api/v1/analyze",
        files={"file": ("large.wav", oversized_bytes, "audio/wav")}
    )
    assert response.status_code == 413
    data = response.json()
    assert data["error"]["code"] == "PAYLOAD_TOO_LARGE"


def test_unsupported_extension_rejected(client):
    response = client.post(
        "/api/v1/analyze",
        files={"file": ("script.exe", b"binary_content", "application/octet-stream")}
    )
    assert response.status_code in (400, 415)
    data = response.json()
    assert "error" in data or "detail" in data


def test_missing_filename_rejected(client):
    response = client.post(
        "/api/v1/analyze",
        files={"file": ("", b"audio_content", "audio/wav")}
    )
    assert response.status_code in (400, 422)


def test_extremely_long_filename_rejected(client):
    long_filename = "a" * 300 + ".wav"
    response = client.post(
        "/api/v1/analyze",
        files={"file": (long_filename, b"audio_content", "audio/wav")}
    )
    assert response.status_code == 400


def test_path_traversal_filename_sanitized(client):
    wav_bytes = create_synthetic_wav_bytes(sample_rate=16000, duration=1.0)
    response = client.post(
        "/api/v1/analyze",
        files={"file": ("../../etc/passwd.wav", wav_bytes, "audio/wav")}
    )
    assert response.status_code == 200
    assert "risk_score" in response.json()


def test_custom_x_request_id_passed_and_sanitized(client):
    custom_id = "test-custom-request-id-12345"
    response = client.get("/api/v1/health", headers={"X-Request-ID": custom_id})

    assert response.status_code == 200
    assert response.headers.get("X-Request-ID") == custom_id


def test_malicious_x_request_id_replaced(client):
    malicious_id = "bad_id_<script>alert(1)</script>"
    response = client.get("/api/v1/health", headers={"X-Request-ID": malicious_id})

    assert response.status_code == 200
    returned_id = response.headers.get("X-Request-ID")
    assert returned_id != malicious_id
    assert len(returned_id) > 0


def test_security_headers_present(client):
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"


def test_ready_endpoint_status(client):
    response = client.get("/api/v1/ready")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["detector_ready"] is True
    assert data["replay_dsp_ready"] is True


def test_rate_limiter_allows_under_limit(client):
    for _ in range(5):
        res = client.get("/api/v1/health")
        assert res.status_code == 200
