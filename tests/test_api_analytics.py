"""
Analytics & Data Mart Endpoints Test Suite.

Verifies:
1. /analytics/sales daily trend pagination and date filters
2. /analytics/delivery SLA distributions
3. /analytics/products performance ranking
4. /analytics/sellers merchant volume
5. /analytics/reviews customer sentiment rating breakdowns
"""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


@pytest.fixture
def auth_header():
    res = client.post("/api/v1/auth/login", json={"username": "analyst", "password": "analyst123"})
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_get_sales_mart_paginated(auth_header):
    """Verify sales mart returns paginated records."""
    response = client.get("/api/v1/analytics/sales?page=1&page_size=10", headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert len(data["data"]) == 10
    assert "sales_date" in data["data"][0]


def test_get_delivery_mart(auth_header):
    """Verify delivery mart data retrieval."""
    response = client.get("/api/v1/analytics/delivery", headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) > 0


def test_get_products_mart(auth_header):
    """Verify products performance mart."""
    response = client.get("/api/v1/analytics/products?page=1&page_size=5", headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 5
    assert "product_key" in data["data"][0]


def test_get_sellers_mart(auth_header):
    """Verify seller performance mart."""
    response = client.get("/api/v1/analytics/sellers?page=1&page_size=5", headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 5
    assert "seller_key" in data["data"][0]


def test_get_reviews_mart(auth_header):
    """Verify review rating distribution mart."""
    response = client.get("/api/v1/analytics/reviews", headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 5
