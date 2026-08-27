import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings


@pytest.fixture
def client():
    return TestClient(app)


def test_openapi_schema_generation(client):
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200

    schema = response.json()
    assert schema["info"]["title"] == settings.PROJECT_NAME
    assert schema["info"]["version"] == settings.VERSION
    assert "openapi" in schema

    paths = schema["paths"]
    assert "/api/v1/health" in paths
    assert "/api/v1/ready" in paths
    assert "/api/v1/analyze" in paths

    analyze_post = paths["/api/v1/analyze"]["post"]
    assert "summary" in analyze_post
    assert "responses" in analyze_post
    assert "200" in analyze_post["responses"]
    assert "413" in analyze_post["responses"]
    assert "415" in analyze_post["responses"]


def test_swagger_docs_endpoint(client):
    response = client.get("/api/v1/docs")
    assert response.status_code == 200
    assert "swagger" in response.text.lower() or "html" in response.text.lower()


def test_redoc_endpoint(client):
    response = client.get("/api/v1/redoc")
    assert response.status_code == 200
    assert "redoc" in response.text.lower() or "html" in response.text.lower()
