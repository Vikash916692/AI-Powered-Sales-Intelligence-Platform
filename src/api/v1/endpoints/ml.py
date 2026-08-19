"""
Machine Learning Endpoints: Delay Prediction, Forecasting, Recommendations, Sentiment.
"""

from fastapi import APIRouter, Depends

from src.agents.tools.ml_tools import (
    tool_analyze_review_sentiment,
    tool_forecast_sales,
    tool_predict_delivery_delay,
    tool_recommend_products,
)
from src.api.cache import cached
from src.api.dependencies import get_current_user
from src.api.schemas.auth_schemas import UserRead
from src.api.schemas.ml_schemas import (
    DeliveryDelayRequest,
    DeliveryDelayResponse,
    ForecastRequest,
    ForecastResponse,
    RecommendRequest,
    RecommendResponse,
    SentimentRequest,
    SentimentResponse,
)

router = APIRouter(prefix="/ml", tags=["Machine Learning & Predictive Analytics"])


@router.post(
    "/predict-delay",
    response_model=DeliveryDelayResponse,
    summary="Predict shipment delivery delay probability and risk tier",
)
def predict_delivery_delay(
    request: DeliveryDelayRequest,
    current_user: UserRead = Depends(get_current_user),
):
    """
    Evaluates order shipment features (weight, dimensions, freight cost, origin/destination states)
    and predicts delay probability and operational logistics risk tier.
    """
    res = tool_predict_delivery_delay(
        price=request.price,
        freight_value=request.freight_value,
        product_weight_g=request.product_weight_g,
        product_length_cm=request.product_length_cm,
        product_height_cm=request.product_height_cm,
        product_width_cm=request.product_width_cm,
        estimated_delivery_days=request.estimated_delivery_days,
        customer_state=request.customer_state,
        seller_state=request.seller_state,
        category_name_english=request.category_name_english,
    )
    return DeliveryDelayResponse(**res)


@router.post(
    "/forecast",
    response_model=ForecastResponse,
    summary="Generate forward-looking daily sales revenue demand forecasts",
)
@cached(ttl_seconds=300, key_prefix="ml_forecast")
def forecast_sales(
    request: ForecastRequest,
    current_user: UserRead = Depends(get_current_user),
):
    """
    Generates multi-step recursive daily revenue forecasts for 7 to 90 days
    forward with 95% confidence intervals.
    """
    res = tool_forecast_sales(horizon_days=request.horizon_days)
    return ForecastResponse(**res)


@router.post(
    "/recommend",
    response_model=RecommendResponse,
    summary="Get cross-sell complementary item recommendations",
)
@cached(ttl_seconds=300, key_prefix="ml_recs")
def recommend_products(
    request: RecommendRequest,
    current_user: UserRead = Depends(get_current_user),
):
    """
    Recommends top N complementary products to drive basket size and cross-sell conversions.
    """
    res = tool_recommend_products(product_id=request.product_id, top_n=request.top_n)
    return RecommendResponse(**res)


@router.post(
    "/sentiment",
    response_model=SentimentResponse,
    summary="Classify customer review text sentiment and urgent complaints",
)
def analyze_review_sentiment(
    request: SentimentRequest,
    current_user: UserRead = Depends(get_current_user),
):
    """
    Analyzes Portuguese customer review text, scores complaint probability,
    and flags urgent support intervention requirements.
    """
    res = tool_analyze_review_sentiment(review_text=request.review_text)
    return SentimentResponse(**res)
