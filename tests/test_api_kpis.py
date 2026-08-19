"""
KPI Endpoints Test Suite.

Verifies:
1. /kpis/executive overview metrics and structure
2. /kpis/customer-economics repeat buying rates
3. /kpis/logistics-sla delivery SLA percentages
4. /kpis/rfm customer segments breakdown
5. /kpis/top-categories category rankings
"""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


@pytest.fixture
def auth_header():
    """Provides valid JWT Bearer header."""
    res = client.post("/api/v1/auth/login", json={"username": "executive", "password": "executive123"})
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_get_executive_overview_endpoint(auth_header):
    """Verify executive KPI endpoint returns valid values."""
    response = client.get("/api/v1/kpis/executive", headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert data["total_gross_revenue"] > 1000000.0
    assert data["total_orders"] > 50000
    assert data["executive_aov"] > 50.0
    assert "X-Process-Time" in response.headers


def test_get_customer_economics_endpoint(auth_header):
    """Verify customer repeat rates and economics."""
    response = client.get("/api/v1/kpis/customer-economics", headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert data["total_customers"] > 50000
    assert data["repeat_purchase_rate_pct"] >= 0.0


def test_get_logistics_sla_endpoint(auth_header):
    """Verify logistics SLA endpoint."""
    response = client.get("/api/v1/kpis/logistics-sla", headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert data["on_time_delivery_rate_pct"] > 80.0


def test_get_rfm_segments_endpoint(auth_header):
    """Verify RFM customer segment distribution."""
    response = client.get("/api/v1/kpis/rfm", headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_get_top_categories_endpoint(auth_header):
    """Verify top category ranking endpoint."""
    response = client.get("/api/v1/kpis/top-categories?limit=5", headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 5
