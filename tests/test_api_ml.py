"""
Machine Learning API Endpoints Test Suite.

Verifies:
1. /ml/predict-delay logistics risk scoring
2. /ml/forecast 30/60/90-day forward demand forecasting
3. /ml/recommend cross-sell complementary products
4. /ml/sentiment customer review text NLP classification
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


def test_api_predict_delay(auth_header):
    """Verify delivery delay risk prediction endpoint."""
    response = client.post(
        "/api/v1/ml/predict-delay",
        headers=auth_header,
        json={
            "price": 150.0,
            "freight_value": 28.50,
            "product_weight_g": 1800.0,
            "product_length_cm": 25.0,
            "product_height_cm": 15.0,
            "product_width_cm": 20.0,
            "estimated_delivery_days": 18.0,
            "customer_state": "RJ",
            "seller_state": "SP",
            "category_name_english": "health_beauty",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert 0.0 <= data["delay_probability"] <= 1.0
    assert "Risk" in data["logistics_risk_tier"]


def test_api_forecast_sales(auth_header):
    """Verify forward sales demand forecasting endpoint."""
    response = client.post(
        "/api/v1/ml/forecast",
        headers=auth_header,
        json={"horizon_days": 30},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["horizon_days"] == 30
    assert data["total_projected_revenue"] > 0
    assert len(data["daily_forecasts"]) == 30


def test_api_recommend_products(auth_header):
    """Verify product recommendation cross-sell endpoint."""
    response = client.post(
        "/api/v1/ml/recommend",
        headers=auth_header,
        json={"top_n": 4},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["recommendations_count"] == 4
    assert len(data["recommendations"]) == 4


def test_api_analyze_sentiment(auth_header):
    """Verify review sentiment NLP classification endpoint."""
    response = client.post(
        "/api/v1/ml/sentiment",
        headers=auth_header,
        json={"review_text": "Excelente produto, entrega no prazo e super bem embalado!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "sentiment_tier" in data
    assert data["is_complaint_predicted"] == 0
