USE sales_intelligence;

-- ============================================================
-- PHASE 2 - STEP 2.3
-- CUSTOMER ANALYTICS
-- ============================================================


-- ------------------------------------------------------------
-- CUSTOMER KPI CALCULATIONS
-- ------------------------------------------------------------

-- Total customers
UPDATE kpi_summary
SET kpi_value = (
    SELECT COUNT(DISTINCT customer_key)
    FROM fact_sales
)
WHERE kpi_name = 'total_customers';


-- Repeat customers
UPDATE kpi_summary
SET kpi_value = (
    SELECT COUNT(*)
    FROM (
        SELECT customer_key
        FROM fact_sales
        GROUP BY customer_key
        HAVING COUNT(DISTINCT order_id) > 1
    ) x
)
WHERE kpi_name = 'repeat_customers';


-- Repeat customer rate
UPDATE kpi_summary
SET kpi_value = (
    SELECT
        CASE
            WHEN COUNT(DISTINCT customer_key) = 0 THEN 0
            ELSE
                100.0 *
                COUNT(DISTINCT CASE
                    WHEN order_count > 1 THEN customer_key
                END)
                / COUNT(DISTINCT customer_key)
        END
    FROM (
        SELECT
            customer_key,
            COUNT(DISTINCT order_id) AS order_count
        FROM fact_sales
        GROUP BY customer_key
    ) x
)
WHERE kpi_name = 'repeat_customer_rate';


-- ------------------------------------------------------------
-- CUSTOMER PERFORMANCE TABLE
-- ------------------------------------------------------------

DROP TABLE IF EXISTS customer_performance;

CREATE TABLE customer_performance AS
SELECT
    customer_key,

    COUNT(DISTINCT order_id) AS total_orders,

    COUNT(*) AS total_items,

    ROUND(SUM(price), 2) AS total_revenue,

    ROUND(SUM(freight_value), 2) AS total_freight,

    ROUND(SUM(total_item_value), 2) AS total_sales_value,

    ROUND(
        SUM(price) / NULLIF(COUNT(DISTINCT order_id), 0),
        2
    ) AS average_order_value,

    MIN(purchase_timestamp) AS first_purchase,

    MAX(purchase_timestamp) AS last_purchase,

    DATEDIFF(
        MAX(purchase_timestamp),
        MIN(purchase_timestamp)
    ) AS customer_lifetime_days

FROM fact_sales

GROUP BY customer_key;


-- ------------------------------------------------------------
-- DISPLAY TOP CUSTOMERS
-- ------------------------------------------------------------

SELECT
    customer_key,
    total_orders,
    total_items,
    total_revenue,
    total_sales_value,
    average_order_value,
    first_purchase,
    last_purchase,
    customer_lifetime_days
FROM customer_performance
ORDER BY total_revenue DESC
LIMIT 20;