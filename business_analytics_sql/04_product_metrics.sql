USE sales_intelligence;

-- ============================================================
-- PHASE 2 - STEP 2.4
-- PRODUCT ANALYTICS
-- ============================================================


DROP TABLE IF EXISTS product_performance;

CREATE TABLE product_performance AS
SELECT
    product_key,

    COUNT(*) AS items_sold,

    COUNT(DISTINCT order_id) AS total_orders,

    COUNT(DISTINCT customer_key) AS unique_customers,

    COUNT(DISTINCT seller_key) AS unique_sellers,

    ROUND(SUM(price), 2) AS total_revenue,

    ROUND(SUM(freight_value), 2) AS total_freight,

    ROUND(SUM(total_item_value), 2) AS total_sales_value,

    ROUND(AVG(price), 2) AS average_price,

    ROUND(
        SUM(price) / NULLIF(COUNT(*), 0),
        2
    ) AS revenue_per_item

FROM fact_sales

GROUP BY product_key;


-- ------------------------------------------------------------
-- TOP PRODUCTS BY REVENUE
-- ------------------------------------------------------------

SELECT
    product_key,
    items_sold,
    total_orders,
    unique_customers,
    total_revenue,
    total_sales_value,
    average_price
FROM product_performance
ORDER BY total_revenue DESC
LIMIT 20;


-- ------------------------------------------------------------
-- TOP PRODUCTS BY UNITS SOLD
-- ------------------------------------------------------------

SELECT
    product_key,
    items_sold,
    total_revenue,
    average_price
FROM product_performance
ORDER BY items_sold DESC
LIMIT 20;