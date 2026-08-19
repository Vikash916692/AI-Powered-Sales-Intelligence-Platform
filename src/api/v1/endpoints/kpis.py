"""
Executive KPI Endpoints: Overview, Customer Economics, Logistics SLA, and RFM.
"""


from fastapi import APIRouter, Depends

from src.agents.kpi_engine import kpi_engine
from src.api.cache import cached
from src.api.dependencies import get_current_user
from src.api.schemas.auth_schemas import UserRead
from src.api.schemas.kpi_schemas import (
    CustomerEconomicsResponse,
    ExecutiveOverviewResponse,
    LogisticsSLAResponse,
    RFMSegmentItem,
    TopCategoryItem,
)

router = APIRouter(prefix="/kpis", tags=["Executive KPIs & Benchmarks"])


@router.get(
    "/executive",
    response_model=ExecutiveOverviewResponse,
    summary="Get executive sales overview KPIs (Revenue, Orders, AOV)",
)
@cached(ttl_seconds=300, key_prefix="kpi_overview")
def get_executive_overview(
    current_user: UserRead = Depends(get_current_user),
):
    """
    Computes top-line executive figures: Total Gross Revenue, Total Orders,
    Total Items Sold, AOV, and Active Customer/Seller Ecosystem counts.
    """
    return kpi_engine.get_executive_overview()


@router.get(
    "/customer-economics",
    response_model=CustomerEconomicsResponse,
    summary="Get customer acquisition, repeat purchase rate, and LTV",
)
@cached(ttl_seconds=300, key_prefix="kpi_customer")
def get_customer_economics(
    current_user: UserRead = Depends(get_current_user),
):
    """Calculates customer repeat buying rates, one-time vs repeat split, and mean LTV."""
    return kpi_engine.get_customer_economics()


@router.get(
    "/logistics-sla",
    response_model=LogisticsSLAResponse,
    summary="Get logistics SLA compliance and delivery latency metrics",
)
@cached(ttl_seconds=300, key_prefix="kpi_sla")
def get_logistics_sla(
    current_user: UserRead = Depends(get_current_user),
):
    """Calculates on-time delivery rates, average delivery days, and delay frequency."""
    return kpi_engine.get_logistics_sla()


@router.get(
    "/rfm",
    response_model=list[RFMSegmentItem],
    summary="Get RFM customer quintile segment breakdown",
)
@cached(ttl_seconds=300, key_prefix="kpi_rfm")
def get_rfm_segments(
    current_user: UserRead = Depends(get_current_user),
):
    """Returns customer distribution, cumulative spend, and mean recency across all 10 RFM segments."""
    return kpi_engine.get_rfm_segmentation()


@router.get(
    "/top-categories",
    response_model=list[TopCategoryItem],
    summary="Get top revenue-generating product categories",
)
@cached(ttl_seconds=300, key_prefix="kpi_top_cats")
def get_top_categories(
    limit: int = 5,
    current_user: UserRead = Depends(get_current_user),
):
    """Returns top N product categories ranked by cumulative sales revenue."""
    return kpi_engine.get_top_categories(top_n=limit)
