USE sales_intelligence;

-- ============================================================
-- PHASE 2 - STEP 2.5
-- SELLER ANALYTICS
-- ============================================================


DROP TABLE IF EXISTS seller_performance;

CREATE TABLE seller_performance AS
SELECT
    seller_key,

    COUNT(*) AS items_sold,

    COUNT(DISTINCT order_id) AS total_orders,

    COUNT(DISTINCT customer_key) AS unique_customers,

    COUNT(DISTINCT product_key) AS unique_products,

    ROUND(SUM(price), 2) AS total_revenue,

    ROUND(SUM(freight_value), 2) AS total_freight,

    ROUND(SUM(total_item_value), 2) AS total_sales_value,

    ROUND(AVG(price), 2) AS average_item_price,

    ROUND(
        SUM(price) / NULLIF(COUNT(DISTINCT order_id), 0),
        2
    ) AS average_order_value

FROM fact_sales

GROUP BY seller_key;


-- ------------------------------------------------------------
-- TOP SELLERS
-- ------------------------------------------------------------

SELECT
    seller_key,
    total_orders,
    items_sold,
    unique_customers,
    unique_products,
    total_revenue,
    total_sales_value,
    average_order_value
FROM seller_performance
ORDER BY total_revenue DESC
LIMIT 20;