"""
Automated Test Suite for High-Accuracy Machine Learning Suite.
Verifies:
1. Database Connectivity & Mart Loaders
2. Robust Preprocessor
3. Delivery Delay & Logistics SLA Predictor
4. Multi-Horizon Sales & Demand Forecaster
5. Product Recommendation Engine & Cross-Sell
6. Customer Review Sentiment & Complaint NLP Classifier
"""

import sys
from pathlib import Path

import pandas as pd
import pytest

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from ml.common.data_loader import DataLoader
from ml.common.db import execute_query
from ml.common.preprocessing import RobustPreprocessor
from ml.delivery_delay.predict import DeliveryDelayPredictor
from ml.forecasting.predict import SalesForecaster
from ml.recommendation.predict import RecommendationEngine
from ml.review_sentiment.predict import ReviewSentimentPredictor


def test_database_connection():
    """Verify database connection succeeds."""
    df = execute_query("SELECT DATABASE() AS db_name;")
    assert not df.empty
    assert df["db_name"].iloc[0] == "sales_intelligence"


def test_data_loader_marts():
    """Verify analytical data marts can be loaded."""
    seller_df = DataLoader.load_seller_mart()
    assert not seller_df.empty
    assert "seller_key" in seller_df.columns

    cust_df = DataLoader.load_customer_mart()
    assert not cust_df.empty
    assert "customer_key" in cust_df.columns

    prod_df = DataLoader.load_product_mart()
    assert not prod_df.empty
    assert "product_key" in prod_df.columns


def test_robust_preprocessor():
    """Verify preprocessor handles numeric scaling and imputation without leakage."""
    sample_df = pd.DataFrame({
        "num1": [10.0, 20.0, None, 40.0],
        "num2": [1.0, 2.0, 3.0, 4.0],
    })
    prep = RobustPreprocessor(numeric_features=["num1", "num2"], scaler_type="robust")
    transformed = prep.fit_transform(sample_df)
    assert transformed.shape == (4, 2)
    assert not pd.isna(transformed).any()


def test_delivery_delay_inference():
    """Verify Delivery Delay model produces calibrated risk scores and operational tiers."""
    predictor = DeliveryDelayPredictor()
    scores = predictor.predict_sample(limit=5)
    assert not scores.empty
    assert "delay_probability" in scores.columns
    assert "is_delay_predicted" in scores.columns
    assert "logistics_risk_tier" in scores.columns
    assert (scores["delay_probability"] >= 0.0).all() and (scores["delay_probability"] <= 1.0).all()
    assert all("Risk" in t for t in scores["logistics_risk_tier"])


def test_forecasting_inference():
    """Verify Multi-Step Forecaster produces valid 30-day forward revenue bounds."""
    forecaster = SalesForecaster()
    forecast = forecaster.forecast_future(horizon_days=30)
    assert len(forecast) == 30
    assert "forecast_date" in forecast.columns
    assert "yhat" in forecast.columns
    assert "yhat_lower" in forecast.columns
    assert "yhat_upper" in forecast.columns
    assert (forecast["yhat_upper"] >= forecast["yhat"]).all()
    assert (forecast["yhat"] >= forecast["yhat_lower"]).all()
    assert (forecast["yhat"] >= 0.0).all()


def test_recommendation_inference():
    """Verify Recommendation Engine produces cross-sell products."""
    engine = RecommendationEngine()
    test_pid = engine.global_top_10[0]
    recs = engine.recommend_for_product(test_pid, top_n=3)
    assert len(recs) == 3
    assert all("product_id" in r for r in recs)
    assert all("similarity_score" in r for r in recs)


def test_review_sentiment_inference():
    """Verify Review Sentiment NLP Classifier categorizes text feedback."""
    predictor = ReviewSentimentPredictor()
    sample_texts = [
        "Produto excelente, adorei!",
        "Não recebi o produto, atraso absurdo!",
    ]
    scores = predictor.predict_text(sample_texts)
    assert len(scores) == 2
    assert "complaint_probability" in scores.columns
    assert "sentiment_tier" in scores.columns
    assert scores["is_complaint_predicted"].iloc[1] == 1
    assert scores["is_complaint_predicted"].iloc[0] == 0


if __name__ == "__main__":
    pytest.main(["-v", __file__])
