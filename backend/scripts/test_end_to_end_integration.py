"""
VoxShield End-to-End Backend <-> Frontend Integration Test Script.

Sends a physical ASVspoof 2019 LA audio file to the FastAPI /api/v1/analyze endpoint
using Starlette TestClient and HTTPX, verifying the complete real inference pipeline:
HTTP POST Payload -> FastAPI Router -> Validation -> AudioProcessor -> FeatureExtractor
-> VoiceAntiSpoofingDetector PyTorch Inference -> ReplayDetector -> RiskEvaluator -> AnalysisResponse JSON
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app


def test_end_to_end_audio_analysis():
    print("========================================================")
    print("VOXSHIELD END-TO-END INTEGRATION TEST (REAL AUDIO)")
    print("========================================================")

    test_flac = os.path.abspath("datasets/ASVspoof2019_LA/LA/ASVspoof2019_LA_train/flac/LA_T_1138215.flac")
    if not os.path.exists(test_flac):
        print(f"Error: Physical test audio file {test_flac} not found.")
        sys.exit(1)

    print(f"1. Test Audio File: {os.path.basename(test_flac)} ({os.path.getsize(test_flac)} bytes)")

    client = TestClient(app)

    # Health check probe
    health_resp = client.get("/api/v1/health")
    assert health_resp.status_code == 200
    print(f"2. Health Check Probe: {health_resp.json()}")

    # Readiness check probe
    ready_resp = client.get("/api/v1/ready")
    assert ready_resp.status_code == 200
    print(f"3. Readiness Probe: {ready_resp.json()}")

    # End-to-end audio analysis request
    with open(test_flac, "rb") as f:
        files = {"file": ("LA_T_1138215.flac", f, "audio/flac")}
        response = client.post("/api/v1/analyze", files=files)

    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.text}"

    data = response.json()
    print("\n--- REAL END-TO-END BACKEND RESPONSE JSON ---")
    print(f"  synthetic_score  : {data.get('synthetic_score')}")
    print(f"  replay_score     : {data.get('replay_score')}")
    print(f"  risk_score       : {data.get('risk_score')}")
    print(f"  status           : {data.get('status')}")
    print(f"  verdict          : {data.get('verdict')}")
    print(f"  risk_level       : {data.get('risk_level')}")
    print(f"  confidence       : {data.get('confidence')}")
    print(f"  reasons count    : {len(data.get('reasons', []))}")
    print(f"  forensic stages  : {len(data.get('forensic_timeline', []))}")
    print("--------------------------------------------------------")

    # Schema Assertions
    assert "synthetic_score" in data
    assert 0.0 <= data["synthetic_score"] <= 1.0
    assert "replay_score" in data
    assert 0.0 <= data["replay_score"] <= 1.0
    assert "risk_score" in data
    assert 0.0 <= data["risk_score"] <= 1.0
    assert data["status"] in ["SAFE", "SUSPICIOUS", "HIGH_RISK"]
    assert isinstance(data["reasons"], list)
    assert len(data["reasons"]) > 0

    print("ALL END-TO-END SCHEMAS & REAL INFERENCE VERIFIED: PASS")
    print("========================================================")


if __name__ == "__main__":
    test_end_to_end_audio_analysis()
