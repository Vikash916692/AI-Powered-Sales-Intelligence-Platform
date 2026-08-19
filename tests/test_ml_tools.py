"""
ML Tools Connector Test Suite.

Verifies:
1. Delivery Delay Predictor Tool
2. Sales Forecaster Tool (30-day forward)
3. Product Recommender Tool
4. Review Sentiment NLP Tool
"""

from src.agents.tools.ml_tools import (
    tool_analyze_review_sentiment,
    tool_forecast_sales,
    tool_predict_delivery_delay,
    tool_recommend_products,
)
from src.provenance.tracker import ProvenanceTracker


def test_tool_predict_delivery_delay():
    """Verify tool produces delay probability and logistics tier."""
    tracker = ProvenanceTracker()
    res = tool_predict_delivery_delay(
        freight_value=25.0,
        product_weight_g=1500.0,
        customer_state="RJ",
        seller_state="SP",
        tracker=tracker,
    )
    assert res["status"] == "success"
    assert 0.0 <= res["delay_probability"] <= 1.0
    assert "Risk" in res["logistics_risk_tier"]
    assert len(tracker.evidence) == 1
    assert tracker.evidence[0].evidence_type == "ML_INFERENCE"


def test_tool_forecast_sales():
    """Verify tool generates forward revenue forecast."""
    tracker = ProvenanceTracker()
    res = tool_forecast_sales(horizon_days=30, tracker=tracker)
    assert res["status"] == "success"
    assert res["horizon_days"] == 30
    assert res["total_projected_revenue"] > 0
    assert len(res["daily_forecasts"]) == 30
    assert len(tracker.evidence) == 1


def test_tool_recommend_products():
    """Verify tool returns cross-sell recommendations."""
    tracker = ProvenanceTracker()
    res = tool_recommend_products(top_n=3, tracker=tracker)
    assert res["status"] == "success"
    assert res["recommendations_count"] == 3
    assert len(res["recommendations"]) == 3
    assert len(tracker.evidence) == 1


def test_tool_analyze_review_sentiment():
    """Verify tool identifies complaints and customer sentiment."""
    tracker = ProvenanceTracker()
    res = tool_analyze_review_sentiment("Péssimo serviço, meu pedido atrasou mais de 2 semanas!", tracker=tracker)
    assert res["status"] == "success"
    assert res["is_complaint_predicted"] == 1
    assert res["urgent_action_required"] is True
    assert len(tracker.evidence) == 1
