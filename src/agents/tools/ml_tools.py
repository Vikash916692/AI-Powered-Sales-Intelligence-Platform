"""
Predictive Machine Learning Tools for Agentic AI.

Wraps the 4 Phase 3 high-accuracy ML models:
1. Delivery Delay & SLA Predictor
2. Multi-Horizon Sales & Demand Forecaster
3. Product Recommendation & Cross-Sell Engine
4. Customer Review Sentiment & Complaint Classifier
"""

import time
from typing import Any

import pandas as pd

from ml.delivery_delay.predict import DeliveryDelayPredictor
from ml.forecasting.predict import SalesForecaster
from ml.recommendation.predict import RecommendationEngine
from ml.review_sentiment.predict import ReviewSentimentPredictor
from src.provenance.tracker import ProvenanceTracker

# Lazy loaded model singletons
_delay_predictor: DeliveryDelayPredictor | None = None
_forecaster: SalesForecaster | None = None
_recommender: RecommendationEngine | None = None
_sentiment_predictor: ReviewSentimentPredictor | None = None


def get_delay_predictor() -> DeliveryDelayPredictor:
    global _delay_predictor
    if _delay_predictor is None:
        _delay_predictor = DeliveryDelayPredictor()
    return _delay_predictor


def get_forecaster() -> SalesForecaster:
    global _forecaster
    if _forecaster is None:
        _forecaster = SalesForecaster()
    return _forecaster


def get_recommender() -> RecommendationEngine:
    global _recommender
    if _recommender is None:
        _recommender = RecommendationEngine()
    return _recommender


def get_sentiment_predictor() -> ReviewSentimentPredictor:
    global _sentiment_predictor
    if _sentiment_predictor is None:
        _sentiment_predictor = ReviewSentimentPredictor()
    return _sentiment_predictor


def tool_predict_delivery_delay(
    price: float = 120.0,
    freight_value: float = 20.0,
    product_weight_g: float = 1000.0,
    product_length_cm: float = 20.0,
    product_height_cm: float = 15.0,
    product_width_cm: float = 15.0,
    estimated_delivery_days: float = 15.0,
    customer_state: str = "SP",
    seller_state: str = "SP",
    category_name_english: str = "bed_bath_table",
    tracker: ProvenanceTracker | None = None,
) -> dict[str, Any]:
    """
    Predicts whether a shipment will be delayed, calculates delay probability,
    and assigns a logistics operational risk tier.
    """
    start_time = time.perf_counter()
    predictor = get_delay_predictor()

    vol_cm3 = float(product_length_cm) * float(product_height_cm) * float(product_width_cm)
    freight_val = float(freight_value)
    item_price = float(price)
    total_val = item_price + freight_val
    freight_ratio = freight_val / total_val if total_val > 0 else 0.15
    is_interstate = int(str(customer_state).upper() != str(seller_state).upper())

    input_df = pd.DataFrame([{
        "price": item_price,
        "freight_value": freight_val,
        "freight_ratio": freight_ratio,
        "product_weight_g": float(product_weight_g),
        "product_volume_cm3": vol_cm3,
        "estimated_delivery_days": float(estimated_delivery_days),
        "is_interstate": is_interstate,
        "purchase_dayofweek": 2,
        "purchase_month": 6,
        "seller_historical_orders": 25.0,
        "seller_avg_order_value": 110.0,
        "customer_state": str(customer_state).upper(),
        "seller_state": str(seller_state).upper(),
        "category_name_english": str(category_name_english).lower(),
    }])

    pred_df = predictor.predict(input_df)
    res = pred_df.iloc[0].to_dict()

    latency_ms = (time.perf_counter() - start_time) * 1000.0

    output = {
        "status": "success",
        "delay_probability": round(float(res.get("delay_probability", 0.0)), 4),
        "is_delay_predicted": int(res.get("is_delay_predicted", 0)),
        "logistics_risk_tier": str(res.get("logistics_risk_tier", "Unknown")),
        "recommendation": (
            "Assign priority carrier dispatch"
            if res.get("delay_probability", 0.0) >= 0.50
            else "Standard carrier routing acceptable"
        ),
    }

    if tracker:
        tracker.record_ml(
            model_name="delivery_delay_predictor",
            inputs=input_df.iloc[0].to_dict(),
            outputs=output,
            confidence=round(1.0 - abs(output["delay_probability"] - 0.5) * 0.5, 2),
            latency_ms=latency_ms,
        )

    return output


def tool_forecast_sales(
    horizon_days: int = 30,
    tracker: ProvenanceTracker | None = None,
) -> dict[str, Any]:
    """
    Generates forward-looking daily sales revenue forecasts with 95% confidence intervals.
    """
    start_time = time.perf_counter()
    forecaster = get_forecaster()
    horizon = min(max(int(horizon_days), 7), 90)

    forecast_df = forecaster.forecast_future(horizon_days=horizon)
    latency_ms = (time.perf_counter() - start_time) * 1000.0

    records = forecast_df.to_dict(orient="records")
    total_projected_revenue = float(forecast_df["yhat"].sum())
    daily_avg_revenue = float(forecast_df["yhat"].mean())

    output = {
        "status": "success",
        "horizon_days": horizon,
        "total_projected_revenue": round(total_projected_revenue, 2),
        "daily_average_projected_revenue": round(daily_avg_revenue, 2),
        "forecast_period_start": str(forecast_df["forecast_date"].iloc[0]),
        "forecast_period_end": str(forecast_df["forecast_date"].iloc[-1]),
        "daily_forecasts": records,
    }

    if tracker:
        tracker.record_ml(
            model_name="sales_forecaster",
            inputs={"horizon_days": horizon},
            outputs={
                "total_projected_revenue": round(total_projected_revenue, 2),
                "horizon_days": horizon,
            },
            confidence=0.88,
            latency_ms=latency_ms,
        )

    return output


def tool_recommend_products(
    product_id: str | None = None,
    top_n: int = 5,
    tracker: ProvenanceTracker | None = None,
) -> dict[str, Any]:
    """
    Recommends high-affinity complementary items for cross-selling and cart completion.
    """
    start_time = time.perf_counter()
    recommender = get_recommender()
    n = min(max(int(top_n), 1), 10)

    if not product_id:
        target_pid = recommender.global_top_10[0]
    else:
        target_pid = str(product_id)

    recs = recommender.recommend_for_product(target_pid, top_n=n)
    latency_ms = (time.perf_counter() - start_time) * 1000.0

    output = {
        "status": "success",
        "query_product_id": target_pid,
        "recommendations_count": len(recs),
        "recommendations": recs,
    }

    if tracker:
        tracker.record_ml(
            model_name="product_recommender",
            inputs={"product_id": target_pid, "top_n": n},
            outputs={"recommendations_count": len(recs)},
            confidence=0.91,
            latency_ms=latency_ms,
        )

    return output


def tool_analyze_review_sentiment(
    review_text: str,
    tracker: ProvenanceTracker | None = None,
) -> dict[str, Any]:
    """
    Classifies customer review text sentiment and flags urgent complaints.
    """
    start_time = time.perf_counter()
    predictor = get_sentiment_predictor()

    pred_df = predictor.predict_text([str(review_text)])
    res = pred_df.iloc[0].to_dict()
    latency_ms = (time.perf_counter() - start_time) * 1000.0

    output = {
        "status": "success",
        "review_text": str(review_text),
        "sentiment_tier": str(res.get("sentiment_tier", "Unknown")),
        "is_complaint_predicted": int(res.get("is_complaint_predicted", 0)),
        "complaint_probability": round(float(res.get("complaint_probability", 0.0)), 4),
        "urgent_action_required": bool(res.get("is_complaint_predicted", 0) == 1),
    }

    if tracker:
        tracker.record_ml(
            model_name="review_sentiment_nlp",
            inputs={"text": str(review_text)[:80]},
            outputs=output,
            confidence=round(float(res.get("complaint_probability", 0.9)), 2),
            latency_ms=latency_ms,
        )

    return output
