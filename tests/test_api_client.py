"""
Automated Test Suite for Dedicated Dashboard API Client.

Verifies:
1. APIClient login and token lifecycle
2. APIClient KPI fetching and deserialization
3. APIClient ML forecasting and delay scoring
4. APIClient Error handling and error propagation
"""

import pytest

from src.dashboard.api_client import APIClientError, SalesIntelligenceAPIClient


def test_api_client_unauthenticated_error():
    """Verify unauthenticated requests raise APIClientError."""
    unauth_client = SalesIntelligenceAPIClient(base_url="http://localhost:8000/api/v1", token=None)
    with pytest.raises(APIClientError) as exc_info:
        unauth_client.get_current_user()
    assert "401" in str(exc_info.value) or "credentials" in str(exc_info.value).lower()


def test_api_client_login_and_kpis():
    """Verify login and fetching executive overview."""
    client = SalesIntelligenceAPIClient(base_url="http://localhost:8000/api/v1")
    login_res = client.login(username="admin", password="admin123")
    assert "access_token" in login_res
    assert client.token is not None

    overview = client.get_executive_overview()
    assert float(overview["total_gross_revenue"]) > 1000000.0
    assert int(overview["total_orders"]) > 50000


def test_api_client_ml_tools():
    """Verify client execution of ML forecast and delay tools."""
    client = SalesIntelligenceAPIClient(base_url="http://localhost:8000/api/v1")
    client.login(username="admin", password="admin123")

    forecast = client.forecast_sales(horizon_days=14)
    assert forecast["horizon_days"] == 14
    assert len(forecast["daily_forecasts"]) == 14

    delay = client.predict_delay({
        "price": 100.0,
        "freight_value": 20.0,
        "product_weight_g": 1000.0,
        "product_length_cm": 20.0,
        "product_height_cm": 15.0,
        "product_width_cm": 15.0,
        "estimated_delivery_days": 15.0,
        "customer_state": "SP",
        "seller_state": "SP",
        "category_name_english": "bed_bath_table",
    })
    assert "delay_probability" in delay
