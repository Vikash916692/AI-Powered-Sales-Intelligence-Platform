USE sales_intelligence;

-- ============================================================
-- PHASE 2 - STEP 2.6
-- GEOGRAPHIC ANALYTICS
-- ============================================================


-- ------------------------------------------------------------
-- CUSTOMER GEOGRAPHY PERFORMANCE
-- ------------------------------------------------------------

DROP TABLE IF EXISTS customer_geography_performance;

CREATE TABLE customer_geography_performance AS
SELECT
    customer_geography_key AS geography_key,

    COUNT(DISTINCT order_id) AS total_orders,

    COUNT(DISTINCT customer_key) AS total_customers,

    COUNT(DISTINCT product_key) AS unique_products,

    ROUND(SUM(price), 2) AS total_revenue,

    ROUND(SUM(freight_value), 2) AS total_freight,

    ROUND(SUM(total_item_value), 2) AS total_sales_value

FROM fact_sales

WHERE customer_geography_key IS NOT NULL

GROUP BY customer_geography_key;


-- ------------------------------------------------------------
-- SELLER GEOGRAPHY PERFORMANCE
-- ------------------------------------------------------------

DROP TABLE IF EXISTS seller_geography_performance;

CREATE TABLE seller_geography_performance AS
SELECT
    seller_geography_key AS geography_key,

    COUNT(DISTINCT order_id) AS total_orders,

    COUNT(DISTINCT seller_key) AS total_sellers,

    COUNT(DISTINCT product_key) AS unique_products,

    ROUND(SUM(price), 2) AS total_revenue,

    ROUND(SUM(freight_value), 2) AS total_freight,

    ROUND(SUM(total_item_value), 2) AS total_sales_value

FROM fact_sales

WHERE seller_geography_key IS NOT NULL

GROUP BY seller_geography_key;


-- ------------------------------------------------------------
-- TOP CUSTOMER GEOGRAPHIES
-- ------------------------------------------------------------

SELECT *
FROM customer_geography_performance
ORDER BY total_revenue DESC
LIMIT 20;


-- ------------------------------------------------------------
-- TOP SELLER GEOGRAPHIES
-- ------------------------------------------------------------

SELECT *
FROM seller_geography_performance
ORDER BY total_revenue DESC
LIMIT 20;