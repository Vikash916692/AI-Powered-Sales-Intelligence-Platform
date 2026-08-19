"""
Pydantic v2 schemas package for API request and response validation.
"""

from src.api.schemas.agent_schemas import (
    AgentQueryRequest,
    AgentQueryResponse,
    EvidenceItemSchema,
)
from src.api.schemas.analytics_schemas import (
    MartQueryFilter,
    PaginatedResponse,
    PaginationParams,
)
from src.api.schemas.auth_schemas import (
    LoginRequest,
    Token,
    TokenPayload,
    UserBase,
    UserCreate,
    UserRead,
)
from src.api.schemas.kpi_schemas import (
    CustomerEconomicsResponse,
    ExecutiveOverviewResponse,
    LogisticsSLAResponse,
    RFMSegmentItem,
    TopCategoryItem,
)
from src.api.schemas.ml_schemas import (
    DailyForecastItem,
    DeliveryDelayRequest,
    DeliveryDelayResponse,
    ForecastRequest,
    ForecastResponse,
    RecommendationItem,
    RecommendRequest,
    RecommendResponse,
    SentimentRequest,
    SentimentResponse,
)
from src.api.schemas.task_schemas import (
    AsyncRCARequest,
    TaskStatusResponse,
)

__all__ = [
    "AgentQueryRequest",
    "AgentQueryResponse",
    "AsyncRCARequest",
    "CustomerEconomicsResponse",
    "DailyForecastItem",
    "DeliveryDelayRequest",
    "DeliveryDelayResponse",
    "EvidenceItemSchema",
    "ExecutiveOverviewResponse",
    "ForecastRequest",
    "ForecastResponse",
    "LoginRequest",
    "LogisticsSLAResponse",
    "MartQueryFilter",
    "PaginatedResponse",
    "PaginationParams",
    "RFMSegmentItem",
    "RecommendRequest",
    "RecommendResponse",
    "RecommendationItem",
    "SentimentRequest",
    "SentimentResponse",
    "TaskStatusResponse",
    "Token",
    "TokenPayload",
    "TopCategoryItem",
    "UserBase",
    "UserCreate",
    "UserRead",
]
