USE sales_intelligence;

-- ============================================================
-- PHASE 2 - STEP 2.12
-- ANALYTICAL DATA MARTS
-- ============================================================


-- ============================================================
-- 1. SALES MART
-- Grain: One row per sales date
-- ============================================================

DROP TABLE IF EXISTS sales_mart;

CREATE TABLE sales_mart AS

SELECT
    DATE(purchase_timestamp) AS sales_date,

    COUNT(DISTINCT order_id) AS total_orders,

    COUNT(*) AS total_items,

    COUNT(DISTINCT customer_key) AS total_customers,

    COUNT(DISTINCT product_key) AS unique_products,

    COUNT(DISTINCT seller_key) AS active_sellers,

    ROUND(SUM(price), 2) AS revenue,

    ROUND(SUM(freight_value), 2) AS freight_revenue,

    ROUND(SUM(total_item_value), 2) AS total_sales_value,

    ROUND(
        SUM(price)
        / NULLIF(COUNT(DISTINCT order_id), 0),
        2
    ) AS average_order_value,

    ROUND(
        AVG(price),
        2
    ) AS average_item_value

FROM fact_sales

WHERE purchase_timestamp IS NOT NULL

GROUP BY DATE(purchase_timestamp);


-- ============================================================
-- 2. CUSTOMER MART
-- Grain: One row per customer
-- ============================================================

DROP TABLE IF EXISTS customer_mart;

CREATE TABLE customer_mart AS

SELECT
    cp.customer_key,

    cp.total_orders,

    cp.total_items,

    cp.total_revenue,

    cp.total_freight,

    cp.total_sales_value,

    cp.average_order_value,

    cp.first_purchase,

    cp.last_purchase,

    cp.customer_lifetime_days,

    CASE
        WHEN cp.total_orders = 1
            THEN 'One-Time Customer'

        WHEN cp.total_orders >= 2
            THEN 'Repeat Customer'

        ELSE 'Other'

    END AS customer_type

FROM customer_performance cp;


-- ============================================================
-- 3. RFM MART
-- Grain: One row per customer
-- ============================================================

DROP TABLE IF EXISTS rfm_mart;

CREATE TABLE rfm_mart AS

SELECT
    customer_key,

    recency,

    frequency,

    monetary_value,

    recency_score,

    frequency_score,

    monetary_score,

    rfm_segment

FROM customer_rfm;


-- ============================================================
-- 4. PRODUCT MART
-- Grain: One row per product
-- ============================================================

DROP TABLE IF EXISTS product_mart;

CREATE TABLE product_mart AS

SELECT
    product_key,

    items_sold,

    total_orders,

    unique_customers,

    unique_sellers,

    total_revenue,

    total_freight,

    total_sales_value,

    average_price,

    revenue_per_item

FROM product_performance;


-- ============================================================
-- 5. SELLER MART
-- Grain: One row per seller
-- ============================================================

DROP TABLE IF EXISTS seller_mart;

CREATE TABLE seller_mart AS

SELECT
    seller_key,

    items_sold,

    total_orders,

    unique_customers,

    unique_products,

    total_revenue,

    total_freight,

    total_sales_value,

    average_item_price,

    average_order_value

FROM seller_performance;


-- ============================================================
-- 6. RETENTION MART
-- Grain: One row per cohort-month combination
-- ============================================================

DROP TABLE IF EXISTS retention_mart;

CREATE TABLE retention_mart AS

SELECT
    cohort_month,

    cohort_month_number,

    active_customers,

    cohort_customers,

    retention_rate

FROM cohort_retention_rate;


-- ============================================================
-- 7. CUSTOMER CONCENTRATION MART
-- Grain: One row per customer
-- ============================================================

DROP TABLE IF EXISTS customer_concentration_mart;

CREATE TABLE customer_concentration_mart AS

SELECT
    customer_key,

    total_revenue,

    customer_rank,

    total_customers,

    cumulative_revenue_percentage,

    top_10_percent_customer

FROM customer_concentration;


-- ============================================================
-- 8. PRODUCT CONCENTRATION MART
-- Grain: One row per product
-- ============================================================

DROP TABLE IF EXISTS product_concentration_mart;

CREATE TABLE product_concentration_mart AS

SELECT
    product_key,

    total_revenue,

    product_rank,

    total_products,

    cumulative_revenue_percentage,

    top_20_percent_product

FROM product_concentration;


-- ============================================================
-- 9. SELLER CONCENTRATION MART
-- Grain: One row per seller
-- ============================================================

DROP TABLE IF EXISTS seller_concentration_mart;

CREATE TABLE seller_concentration_mart AS

SELECT
    seller_key,

    total_revenue,

    seller_rank,

    total_sellers,

    cumulative_revenue_percentage,

    top_10_percent_seller

FROM seller_concentration;


-- ============================================================
-- 10. DELIVERY MART
-- ============================================================

DROP TABLE IF EXISTS delivery_mart;

CREATE TABLE delivery_mart AS

SELECT
    order_status,

    total_orders,

    delivered_orders,

    average_delivery_days,

    average_delivery_delay_days,

    delayed_items

FROM delivery_performance;


-- ============================================================
-- 11. REVIEW MART
-- ============================================================

DROP TABLE IF EXISTS review_mart;

CREATE TABLE review_mart AS

SELECT
    review_score,

    review_count,

    percentage_of_reviews

FROM review_distribution;


-- ============================================================
-- 12. BUSINESS INTELLIGENCE SUMMARY MART
-- ============================================================

DROP TABLE IF EXISTS sales_intelligence_mart;

CREATE TABLE sales_intelligence_mart AS

SELECT
    metric,

    metric_value

FROM sales_intelligence_summary;


-- ============================================================
-- 13. DISPLAY CREATED MARTS
-- ============================================================

SHOW TABLES;