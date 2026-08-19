"""
KPI Response Schemas for Executive Metrics.
"""

from pydantic import BaseModel, Field


class ExecutiveOverviewResponse(BaseModel):
    """Executive Sales Overview KPI schema."""

    total_gross_revenue: float = Field(..., description="Cumulative gross item revenue in USD")
    total_orders: int = Field(..., description="Count of completed orders")
    total_items_sold: int = Field(..., description="Count of items sold")
    total_customer_transactions: int = Field(..., description="Customer transactions count")
    executive_aov: float = Field(..., description="Average order value")
    average_item_value: float = Field(..., description="Average item value")
    total_registered_customers: int | None = Field(None, description="Registered customers")
    total_registered_sellers: int | None = Field(None, description="Registered merchants")


class CustomerEconomicsResponse(BaseModel):
    """Customer acquisition and retention metrics."""

    total_customers: int
    repeat_customers: int
    one_time_customers: int
    repeat_purchase_rate_pct: float = Field(..., description="Repeat customer percentage")
    avg_customer_lifetime_days: float = Field(..., description="Average customer lifetime in days")
    customer_ltv_mean: float = Field(..., description="Mean lifetime value per customer")


class LogisticsSLAResponse(BaseModel):
    """Logistics SLA performance and on-time delivery rates."""

    total_orders: float
    delivered_orders: float
    total_delivered_orders: float | None = None
    on_time_delivery_rate_pct: float = Field(..., description="On-time delivery percentage")
    avg_delivery_days: float = Field(..., description="Mean delivery latency in calendar days")
    avg_delay_variance_days: float = Field(..., description="Mean delay variance in days")
    delayed_items_count: float | None = None


class RFMSegmentItem(BaseModel):
    """Individual RFM segment metric breakdown."""

    rfm_segment: str
    customer_count: int
    customer_share_pct: float
    total_segment_spend: float
    avg_spend_per_customer: float
    avg_recency_days: float


class TopCategoryItem(BaseModel):
    """Top product category performance item."""

    category_name: str
    total_units_sold: int
    total_revenue: float
    avg_category_price: float
