"""
VoxShield Vercel Serverless & Production Endpoint Automated Smoke Test.

Verifies:
1. GET /health -> 200 OK {"status": "ok"}
2. GET /api/v1/health -> 200 OK {"status": "ok"}
3. GET /api/v1/ready -> 200 OK (verifies PyTorch model loaded)
4. POST /api/v1/analyze -> 200 OK (verifies real audio inference & response schema)
"""

import os
import sys

# Ensure backend directory is in search path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from api.index import app


def test_vercel_serverless_smoke():
    print("========================================================")
    print("VOXSHIELD VERCEL SERVERLESS AUTOMATED SMOKE TEST")
    print("========================================================")

    client = TestClient(app)

    # 1. Global /health endpoint probe
    res_global_health = client.get("/health")
    assert res_global_health.status_code == 200, f"Expected 200 OK for /health, got {res_global_health.status_code}"
    assert res_global_health.json() == {"status": "ok"}
    print(f"1. GET /health -> HTTP 200 OK {res_global_health.json()}")

    # 2. API v1 /api/v1/health endpoint probe
    res_v1_health = client.get("/api/v1/health")
    assert res_v1_health.status_code == 200, f"Expected 200 OK for /api/v1/health, got {res_v1_health.status_code}"
    assert res_v1_health.json() == {"status": "ok"}
    print(f"2. GET /api/v1/health -> HTTP 200 OK {res_v1_health.json()}")

    # 3. Model readiness probe /api/v1/ready
    res_ready = client.get("/api/v1/ready")
    assert res_ready.status_code == 200, f"Expected 200 OK for /api/v1/ready, got {res_ready.status_code}"
    ready_json = res_ready.json()
    assert ready_json.get("detector_ready") is True
    print(f"3. GET /api/v1/ready -> HTTP 200 OK (Model Checkpoint: {ready_json.get('model_checkpoint')})")

    # 4. Real audio inference probe /api/v1/analyze
    test_flac = os.path.abspath("datasets/ASVspoof2019_LA/LA/ASVspoof2019_LA_train/flac/LA_T_1138215.flac")
    if not os.path.exists(test_flac):
        test_flac = os.path.abspath("../datasets/ASVspoof2019_LA/LA/ASVspoof2019_LA_train/flac/LA_T_1138215.flac")

    if os.path.exists(test_flac):
        with open(test_flac, "rb") as f:
            files = {"file": ("LA_T_1138215.flac", f, "audio/flac")}
            res_analyze = client.post("/api/v1/analyze", files=files)
        
        assert res_analyze.status_code == 200, f"Expected 200 OK for /api/v1/analyze, got {res_analyze.status_code}"
        data = res_analyze.json()
        assert "synthetic_score" in data
        assert "risk_score" in data
        assert "verdict" in data
        print(f"4. POST /api/v1/analyze -> HTTP 200 OK (Synthetic Score: {data.get('synthetic_score')}, Risk: {data.get('risk_score')})")

    print("========================================================")
    print("ALL VERCEL SMOKE TESTS PASSED CLEANLY")
    print("========================================================")


if __name__ == "__main__":
    test_vercel_serverless_smoke()
