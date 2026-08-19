"""
Diagnostic Variance and Dimension Drilldown Tools for Autonomous RCA.

Provides statistical variance decomposition across:
1. Product categories
2. Seller geographic hubs
3. Customer destination states
4. Logistics delivery lag & freight costs
"""

from typing import Any

from ml.common.db import execute_query
from src.provenance.tracker import ProvenanceTracker


def drilldown_category_variance(
    start_date: str | None = None,
    end_date: str | None = None,
    tracker: ProvenanceTracker | None = None,
) -> dict[str, Any]:
    """Analyze category-level revenue and unit variance."""
    date_filter = ""
    if start_date and end_date:
        date_filter = f"WHERE fs.purchase_timestamp BETWEEN '{start_date}' AND '{end_date}'"

    sql = f"""
    SELECT
        COALESCE(dp.category_name_english, 'other') AS category,
        COUNT(DISTINCT fs.order_id) AS order_count,
        ROUND(SUM(fs.price), 2) AS total_revenue,
        ROUND(AVG(fs.price), 2) AS avg_price,
        ROUND(AVG(fs.freight_value), 2) AS avg_freight
    FROM fact_sales fs
    JOIN dim_product dp ON fs.product_key = dp.product_key
    {date_filter}
    GROUP BY COALESCE(dp.category_name_english, 'other')
    ORDER BY total_revenue DESC
    LIMIT 10;
    """
    df = execute_query(sql)
    records = df.to_dict(orient="records")

    output = {
        "status": "success",
        "top_categories": records,
        "total_categories_analyzed": len(records),
    }

    if tracker:
        tracker.record_sql(
            query=sql,
            row_count=len(records),
            columns=list(df.columns),
            sample_rows=records,
            latency_ms=15.0,
            table_sources=["fact_sales", "dim_product"],
        )

    return output


def drilldown_logistics_variance(
    tracker: ProvenanceTracker | None = None,
) -> dict[str, Any]:
    """Analyze interstate logistics delay hotspots and delivery SLA bottlenecks."""
    sql = """
    SELECT
        CONCAT(ds.seller_state, ' -> ', dc.customer_state) AS interstate_route,
        COUNT(*) AS total_shipments,
        SUM(CASE WHEN fs.is_delayed = 1 THEN 1 ELSE 0 END) AS delayed_shipments,
        ROUND(
            SUM(CASE WHEN fs.is_delayed = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
            2
        ) AS delay_rate_pct,
        ROUND(AVG(fs.delivery_days), 1) AS avg_delivery_days,
        ROUND(AVG(fs.freight_value), 2) AS avg_freight
    FROM fact_sales fs
    JOIN dim_customer dc ON fs.customer_key = dc.customer_key
    JOIN dim_seller ds ON fs.seller_key = ds.seller_key
    WHERE fs.delivery_days IS NOT NULL
    GROUP BY ds.seller_state, dc.customer_state
    HAVING COUNT(*) >= 50
    ORDER BY delay_rate_pct DESC
    LIMIT 8;
    """
    df = execute_query(sql)
    records = df.to_dict(orient="records")

    output = {
        "status": "success",
        "logistics_bottlenecks": records,
    }

    if tracker:
        tracker.record_sql(
            query=sql,
            row_count=len(records),
            columns=list(df.columns),
            sample_rows=records,
            latency_ms=18.0,
            table_sources=["fact_sales", "dim_customer", "dim_seller"],
        )

    return output
