"""
Business knowledge documents containing domain definitions, standard KPI formulas,
RFM segment rules, delivery SLAs, and operational thresholds for the Business RAG collection.
"""


BUSINESS_DOCUMENTS: list[dict[str, str]] = [
    {
        "id": "biz_kpi_definitions",
        "domain": "executive_kpis",
        "category": "formula",
        "text": (
            "Executive Business KPI Formulas & Benchmarks:\n"
            "1. Gross Revenue = SUM(price) across all delivered order items.\n"
            "2. Gross Merchandise Value (GMV) / Total Sales = SUM(price + freight_value).\n"
            "3. Average Order Value (AOV) = SUM(price) / COUNT(DISTINCT order_id).\n"
            "4. Average Item Value (AIV) = SUM(price) / COUNT(order_item_id).\n"
            "5. Repeat Purchase Rate = (Count of Customers with Orders >= 2) / Total Unique Customers * 100.\n"
            "6. On-Time Delivery Rate (SLA) = (Count of Orders where delivery_days <= estimated_delivery_days) / Total Delivered Orders * 100. Target benchmark is >= 92%.\n"
            "7. Average Delivery Latency = AVG(delivery_days) in calendar days from purchase to customer handover."
        ),
    },
    {
        "id": "biz_rfm_segments",
        "domain": "customer_marketing",
        "category": "rules",
        "text": (
            "RFM Customer Segmentation Rules (NTILE(5) Scoring 1 to 5):\n"
            "- Champions: R score 5, F score 4-5, M score 4-5. Bought recently, buy often, and spend the most. Strategy: Reward with VIP perks, early access.\n"
            "- Loyal Customers: R score 3-4, F score 3-5, M score 3-5. Consistent spenders responsive to promotions. Strategy: Upsell higher-value products.\n"
            "- Potential Loyalists: R score 4-5, F score 2-3, M score 2-3. Recent buyers with moderate spend. Strategy: Offer membership or cross-sell.\n"
            "- At Risk: R score 1-2, F score 3-5, M score 3-5. High past value who haven't purchased in a long time. Strategy: Send win-back reactivation campaigns.\n"
            "- Hibernating / Lost: R score 1-2, F score 1-2, M score 1-2. Lowest recency, frequency, and spend. Strategy: Ignore or low-cost automated email."
        ),
    },
    {
        "id": "biz_logistics_sla",
        "domain": "logistics_operations",
        "category": "sla_policy",
        "text": (
            "Delivery SLA Policies & Severity Tiers:\n"
            "- On Time: delivery_delay_days <= 0 (Actual delivery occurred on or before estimated date).\n"
            "- Minor Delay: 1 to 3 days late. Acceptable seasonal fluctuation; automated tracking SMS sent to buyer.\n"
            "- Moderate Delay: 4 to 7 days late. Requires carrier inquiry; potential freight voucher compensation.\n"
            "- Severe Delay: > 7 days late. Triggers escalation to logistics tier-2 support, carrier penalty fee, and priority buyer outreach.\n"
            "- Geographic bottleneck notes: Interstate shipments from São Paulo (SP) to North/Northeast states (BA, CE, PE) have higher baseline lead times (~18-25 days) compared to Southeast routes (SP to SP ~4-7 days)."
        ),
    },
    {
        "id": "biz_pareto_concentration",
        "domain": "revenue_concentration",
        "category": "analytics",
        "text": (
            "Pareto (80/20) Revenue Concentration Analytics:\n"
            "- Top Customers: Typically the top ~10% of customers generate ~25% of cumulative revenue due to high e-commerce one-time buyer skew.\n"
            "- Top Product Categories: Top 3 categories ('bed_bath_table', 'health_beauty', 'sports_leisure') account for ~30% of total revenue.\n"
            "- Top Sellers: Top 10% of merchants fulfill > 65% of all marketplace order volume. Monitoring merchant attrition in this top 10% is critical to platform health."
        ),
    },
    {
        "id": "biz_sentiment_csat",
        "domain": "customer_support",
        "category": "sentiment",
        "text": (
            "Review Sentiment & Customer Satisfaction (CSAT) Rules:\n"
            "- Positive Sentiment: Review score 4 or 5 stars. Strong correlation with on-time delivery (< 10 days).\n"
            "- Neutral Sentiment: Review score 3 stars. Moderate experience, minor delivery delays or product packaging feedback.\n"
            "- Negative Sentiment / Urgent Complaint: Review score 1 or 2 stars. Over 75% of 1-star reviews are caused by delayed delivery, wrong item shipped, or non-delivery. Priority routing flag is automatically set for review text containing keywords like 'não recebi', 'atraso', 'péssimo', 'quebrado'."
        ),
    },
]
