"""
Machine Learning Request and Response Schemas.
"""

from typing import Any

from pydantic import BaseModel, Field


# 1. Delivery Delay Prediction
class DeliveryDelayRequest(BaseModel):
    """Features for scoring shipment delay risk."""

    price: float = Field(default=120.0, ge=0.0, description="Item price in USD")
    freight_value: float = Field(default=20.0, ge=0.0, description="Freight cost in USD")
    product_weight_g: float = Field(default=1000.0, ge=0.0, description="Product weight in grams")
    product_length_cm: float = Field(default=20.0, ge=0.0)
    product_height_cm: float = Field(default=15.0, ge=0.0)
    product_width_cm: float = Field(default=15.0, ge=0.0)
    estimated_delivery_days: float = Field(default=15.0, ge=1.0, description="Promised SLA days")
    customer_state: str = Field(default="SP", description="Destination state code")
    seller_state: str = Field(default="SP", description="Origin merchant state code")
    category_name_english: str = Field(default="bed_bath_table")


class DeliveryDelayResponse(BaseModel):
    """Delay risk probability and logistics operational tier."""

    status: str = "success"
    delay_probability: float = Field(..., description="Calibrated delay probability (0.0 to 1.0)")
    is_delay_predicted: int = Field(..., description="Binary delay prediction (1=delayed, 0=on-time)")
    logistics_risk_tier: str = Field(..., description="Operational tier")
    recommendation: str


# 2. Sales Forecasting
class ForecastRequest(BaseModel):
    """Horizon configuration for forward demand forecasting."""

    horizon_days: int = Field(default=30, ge=7, le=90, description="Forecast horizon in days (7 to 90)")


class DailyForecastItem(BaseModel):
    """Single-day forecasted revenue and confidence intervals."""

    forecast_date: str
    yhat: float = Field(..., description="Point forecast in USD")
    yhat_lower: float = Field(..., description="95% lower bound")
    yhat_upper: float = Field(..., description="95% upper bound")


class ForecastResponse(BaseModel):
    """Aggregated sales demand forecast output."""

    status: str = "success"
    horizon_days: int
    total_projected_revenue: float
    daily_average_projected_revenue: float
    forecast_period_start: str
    forecast_period_end: str
    daily_forecasts: list[dict[str, Any]]


# 3. Product Recommendations
class RecommendRequest(BaseModel):
    """Product identifier for cross-sell recommendations."""

    product_id: str | None = Field(None, description="Natural product ID (defaults to global bestseller if omitted)")
    top_n: int = Field(default=5, ge=1, le=10, description="Number of recommendations (1 to 10)")


class RecommendationItem(BaseModel):
    """Recommended complementary item."""

    product_id: str
    similarity_score: float
    product_category: str | None = None


class RecommendResponse(BaseModel):
    """Cross-sell product recommendations."""

    status: str = "success"
    query_product_id: str
    recommendations_count: int
    recommendations: list[dict[str, Any]]


# 4. Review Sentiment NLP
class SentimentRequest(BaseModel):
    """Customer review text for sentiment NLP classification."""

    review_text: str = Field(
        ...,
        min_length=3,
        max_length=2000,
        description="Raw Portuguese review text",
    )


class SentimentResponse(BaseModel):
    """Review sentiment and priority complaint flag."""

    status: str = "success"
    review_text: str
    sentiment_tier: str
    is_complaint_predicted: int
    complaint_probability: float
    urgent_action_required: bool
