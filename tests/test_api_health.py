"""
Health, Liveness, and Readiness API Test Suite.

Verifies:
1. /health comprehensive component health status
2. /health/live Kubernetes liveness probe
3. /health/ready Kubernetes readiness probe
"""

from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_health_check_endpoint():
    """Verify deep health check passes."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in {"healthy", "degraded"}
    assert "database" in data["components"]
    assert "cache" in data["components"]
    assert "vector_store" in data["components"]
    assert "ml_models" in data["components"]


def test_liveness_probe():
    """Verify Kubernetes liveness probe returns alive."""
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "alive"


def test_readiness_probe():
    """Verify Kubernetes readiness probe returns ready."""
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"
