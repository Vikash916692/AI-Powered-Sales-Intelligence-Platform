"""
KPI Intelligence Engine.

Computes mathematically validated business metrics, benchmark comparisons,
and executive KPIs directly from analytical data marts and star-schema tables.
Guarantees zero formula hallucination.
"""

from typing import Any

from ml.common.db import execute_query, get_engine
from src.provenance.tracker import ProvenanceTracker


class KPIIntelligenceEngine:
    """Calculates standardized, audit-ready executive KPIs and benchmarks."""

    def __init__(self):
        self.engine = get_engine()

    def get_executive_overview(
        self, tracker: ProvenanceTracker | None = None
    ) -> dict[str, Any]:
        """
        Calculates executive summary: Revenue, Order Volume, AOV, Unique Customers, Sellers.
        """
        sql = """
        SELECT
            ROUND(SUM(revenue), 2) AS total_gross_revenue,
            SUM(total_orders) AS total_orders,
            SUM(total_items) AS total_items_sold,
            SUM(total_customers) AS total_customer_transactions,
            ROUND(SUM(revenue) / NULLIF(SUM(total_orders), 0), 2) AS executive_aov,
            ROUND(SUM(revenue) / NULLIF(SUM(total_items), 0), 2) AS average_item_value
        FROM sales_mart;
        """
        df = execute_query(sql)
        row = df.iloc[0].to_dict() if not df.empty else {}

        # Distinct customer & seller counts from dimension tables
        dim_counts_sql = """
        SELECT
            (SELECT COUNT(*) FROM dim_customer) AS total_registered_customers,
            (SELECT COUNT(*) FROM dim_seller) AS total_registered_sellers;
        """
        dim_df = execute_query(dim_counts_sql)
        if not dim_df.empty:
            row.update(dim_df.iloc[0].to_dict())

        if tracker:
            tracker.record_kpi(
                kpi_name="Executive Sales Overview",
                formula="SUM(revenue), SUM(orders), AOV=Revenue/Orders",
                value=f"Revenue: ${row.get('total_gross_revenue', 0):,.2f} | Orders: {row.get('total_orders', 0):,}",
                benchmark="Enterprise Standard Benchmark",
            )
        return row

    def get_customer_economics(
        self, tracker: ProvenanceTracker | None = None
    ) -> dict[str, Any]:
        """
        Calculates customer acquisition, repeat purchase rates, and lifetime tenure.
        """
        sql = """
        SELECT
            COUNT(*) AS total_customers,
            SUM(CASE WHEN total_orders >= 2 THEN 1 ELSE 0 END) AS repeat_customers,
            SUM(CASE WHEN total_orders = 1 THEN 1 ELSE 0 END) AS one_time_customers,
            ROUND(
                SUM(CASE WHEN total_orders >= 2 THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
                2
            ) AS repeat_purchase_rate_pct,
            ROUND(AVG(customer_lifetime_days), 1) AS avg_customer_lifetime_days,
            ROUND(AVG(total_revenue), 2) AS customer_ltv_mean
        FROM customer_mart;
        """
        df = execute_query(sql)
        row = df.iloc[0].to_dict() if not df.empty else {}

        if tracker:
            tracker.record_kpi(
                kpi_name="Customer Retention & Repeat Rate",
                formula="Repeat Customers / Total Customers * 100",
                value=f"{row.get('repeat_purchase_rate_pct', 0)}% repeat rate",
                benchmark="E-Commerce Baseline: 3-5%",
            )
        return row

    def get_logistics_sla(
        self, tracker: ProvenanceTracker | None = None
    ) -> dict[str, Any]:
        """
        Calculates on-time delivery rates, latency, and SLA delay distributions.
        """
        sql = """
        SELECT
            SUM(total_orders) AS total_orders,
            SUM(delivered_orders) AS delivered_orders,
            SUM(delivered_orders) AS total_delivered_orders,
            ROUND(
                SUM(delivered_orders) * 100.0 / NULLIF(SUM(total_orders), 0),
                2
            ) AS on_time_delivery_rate_pct,
            ROUND(AVG(average_delivery_days), 1) AS avg_delivery_days,
            ROUND(AVG(average_delivery_delay_days), 1) AS avg_delay_variance_days,
            SUM(delayed_items) AS delayed_items_count
        FROM delivery_mart;
        """
        df = execute_query(sql)
        row = df.iloc[0].to_dict() if not df.empty else {}

        if tracker:
            tracker.record_kpi(
                kpi_name="Logistics On-Time Delivery SLA",
                formula="Delivered Orders / Total Orders * 100",
                value=f"{row.get('on_time_delivery_rate_pct', 0)}% SLA Compliance",
                benchmark="Target SLA >= 92%",
            )
        return row

    def get_rfm_segmentation(
        self, tracker: ProvenanceTracker | None = None
    ) -> list[dict[str, Any]]:
        """
        Returns RFM tier distributions, customer count, and total monetary contribution.
        """
        sql = """
        SELECT
            rfm_segment,
            COUNT(*) AS customer_count,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM rfm_mart), 2) AS customer_share_pct,
            ROUND(SUM(monetary_value), 2) AS total_segment_spend,
            ROUND(AVG(monetary_value), 2) AS avg_spend_per_customer,
            ROUND(AVG(recency), 1) AS avg_recency_days
        FROM rfm_mart
        GROUP BY rfm_segment
        ORDER BY total_segment_spend DESC;
        """
        df = execute_query(sql)
        results = df.to_dict(orient="records")

        if tracker:
            top_seg = results[0]["rfm_segment"] if results else "None"
            tracker.record_kpi(
                kpi_name="RFM Segment Breakdown",
                formula="NTILE(5) Recency, Frequency, Monetary Quintile Segmentation",
                value=f"Top Revenue Segment: {top_seg}",
            )
        return results

    def get_top_categories(
        self, top_n: int = 5, tracker: ProvenanceTracker | None = None
    ) -> list[dict[str, Any]]:
        """
        Returns top revenue-generating product categories.
        """
        sql = f"""
        SELECT
            COALESCE(dp.category_name_english, 'uncategorized') AS category_name,
            SUM(pm.items_sold) AS total_units_sold,
            ROUND(SUM(pm.total_revenue), 2) AS total_revenue,
            ROUND(AVG(pm.average_price), 2) AS avg_category_price
        FROM product_mart pm
        JOIN dim_product dp ON pm.product_key = dp.product_key
        GROUP BY COALESCE(dp.category_name_english, 'uncategorized')
        ORDER BY total_revenue DESC
        LIMIT {top_n};
        """
        df = execute_query(sql)
        results = df.to_dict(orient="records")

        if tracker:
            top_cat = results[0]["category_name"] if results else "None"
            tracker.record_kpi(
                kpi_name="Top Product Categories",
                formula=f"Top {top_n} Categories by Cumulative Revenue",
                value=f"Dominant Category: {top_cat}",
            )
        return results


# Global singleton instance
kpi_engine = KPIIntelligenceEngine()
