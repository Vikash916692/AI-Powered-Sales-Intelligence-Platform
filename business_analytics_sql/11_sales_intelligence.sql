USE sales_intelligence;

-- ============================================================
-- PHASE 2 - STEP 2.11
-- ADVANCED SALES INTELLIGENCE
-- ============================================================


-- ============================================================
-- 1. CUSTOMER REVENUE CONCENTRATION
-- ============================================================

DROP TABLE IF EXISTS customer_concentration;

CREATE TABLE customer_concentration AS

WITH ranked_customers AS (

    SELECT
        customer_key,
        total_revenue,

        SUM(total_revenue) OVER ()
            AS overall_revenue,

        SUM(total_revenue) OVER (
            ORDER BY total_revenue DESC
            ROWS BETWEEN UNBOUNDED PRECEDING
            AND CURRENT ROW
        ) AS cumulative_revenue,

        ROW_NUMBER() OVER (
            ORDER BY total_revenue DESC
        ) AS customer_rank,

        COUNT(*) OVER () AS total_customers

    FROM customer_performance
)

SELECT

    customer_key,

    total_revenue,

    customer_rank,

    total_customers,

    ROUND(
        100.0 * cumulative_revenue
        / NULLIF(overall_revenue, 0),
        2
    ) AS cumulative_revenue_percentage,

    CASE
        WHEN customer_rank <= CEIL(total_customers * 0.10)
        THEN 1
        ELSE 0
    END AS top_10_percent_customer

FROM ranked_customers;


-- ============================================================
-- 2. PRODUCT REVENUE CONCENTRATION
-- ============================================================

DROP TABLE IF EXISTS product_concentration;

CREATE TABLE product_concentration AS

WITH ranked_products AS (

    SELECT
        product_key,
        total_revenue,

        SUM(total_revenue) OVER ()
            AS overall_revenue,

        SUM(total_revenue) OVER (
            ORDER BY total_revenue DESC
            ROWS BETWEEN UNBOUNDED PRECEDING
            AND CURRENT ROW
        ) AS cumulative_revenue,

        ROW_NUMBER() OVER (
            ORDER BY total_revenue DESC
        ) AS product_rank,

        COUNT(*) OVER () AS total_products

    FROM product_performance
)

SELECT

    product_key,

    total_revenue,

    product_rank,

    total_products,

    ROUND(
        100.0 * cumulative_revenue
        / NULLIF(overall_revenue, 0),
        2
    ) AS cumulative_revenue_percentage,

    CASE
        WHEN product_rank <= CEIL(total_products * 0.20)
        THEN 1
        ELSE 0
    END AS top_20_percent_product

FROM ranked_products;


-- ============================================================
-- 3. SELLER REVENUE CONCENTRATION
-- ============================================================

DROP TABLE IF EXISTS seller_concentration;

CREATE TABLE seller_concentration AS

WITH ranked_sellers AS (

    SELECT
        seller_key,
        total_revenue,

        SUM(total_revenue) OVER ()
            AS overall_revenue,

        SUM(total_revenue) OVER (
            ORDER BY total_revenue DESC
            ROWS BETWEEN UNBOUNDED PRECEDING
            AND CURRENT ROW
        ) AS cumulative_revenue,

        ROW_NUMBER() OVER (
            ORDER BY total_revenue DESC
        ) AS seller_rank,

        COUNT(*) OVER () AS total_sellers

    FROM seller_performance
)

SELECT

    seller_key,

    total_revenue,

    seller_rank,

    total_sellers,

    ROUND(
        100.0 * cumulative_revenue
        / NULLIF(overall_revenue, 0),
        2
    ) AS cumulative_revenue_percentage,

    CASE
        WHEN seller_rank <= CEIL(total_sellers * 0.10)
        THEN 1
        ELSE 0
    END AS top_10_percent_seller

FROM ranked_sellers;


-- ============================================================
-- 4. CUSTOMER CONCENTRATION SUMMARY
-- ============================================================

DROP TABLE IF EXISTS customer_concentration_summary;

CREATE TABLE customer_concentration_summary AS

SELECT

    COUNT(*) AS total_customers,

    SUM(
        CASE
            WHEN top_10_percent_customer = 1
            THEN 1
            ELSE 0
        END
    ) AS top_10_customer_count,

    ROUND(
        SUM(
            CASE
                WHEN top_10_percent_customer = 1
                THEN total_revenue
                ELSE 0
            END
        ),
        2
    ) AS top_10_customer_revenue,

    ROUND(
        100.0 *
        SUM(
            CASE
                WHEN top_10_percent_customer = 1
                THEN total_revenue
                ELSE 0
            END
        )
        /
        NULLIF(SUM(total_revenue), 0),
        2
    ) AS top_10_customer_revenue_percentage

FROM customer_concentration;


-- ============================================================
-- 5. PRODUCT CONCENTRATION SUMMARY
-- ============================================================

DROP TABLE IF EXISTS product_concentration_summary;

CREATE TABLE product_concentration_summary AS

SELECT

    COUNT(*) AS total_products,

    SUM(
        CASE
            WHEN top_20_percent_product = 1
            THEN 1
            ELSE 0
        END
    ) AS top_20_product_count,

    ROUND(
        SUM(
            CASE
                WHEN top_20_percent_product = 1
                THEN total_revenue
                ELSE 0
            END
        ),
        2
    ) AS top_20_product_revenue,

    ROUND(
        100.0 *
        SUM(
            CASE
                WHEN top_20_percent_product = 1
                THEN total_revenue
                ELSE 0
            END
        )
        /
        NULLIF(SUM(total_revenue), 0),
        2
    ) AS top_20_product_revenue_percentage

FROM product_concentration;


-- ============================================================
-- 6. SELLER CONCENTRATION SUMMARY
-- ============================================================

DROP TABLE IF EXISTS seller_concentration_summary;

CREATE TABLE seller_concentration_summary AS

SELECT

    COUNT(*) AS total_sellers,

    SUM(
        CASE
            WHEN top_10_percent_seller = 1
            THEN 1
            ELSE 0
        END
    ) AS top_10_seller_count,

    ROUND(
        SUM(
            CASE
                WHEN top_10_percent_seller = 1
                THEN total_revenue
                ELSE 0
            END
        ),
        2
    ) AS top_10_seller_revenue,

    ROUND(
        100.0 *
        SUM(
            CASE
                WHEN top_10_percent_seller = 1
                THEN total_revenue
                ELSE 0
            END
        )
        /
        NULLIF(SUM(total_revenue), 0),
        2
    ) AS top_10_seller_revenue_percentage

FROM seller_concentration;


-- ============================================================
-- 7. BUSINESS INTELLIGENCE SUMMARY
-- ============================================================

DROP TABLE IF EXISTS sales_intelligence_summary;

CREATE TABLE sales_intelligence_summary AS

SELECT
    'Customer Revenue Concentration' AS metric,
    top_10_customer_revenue_percentage AS metric_value
FROM customer_concentration_summary

UNION ALL

SELECT
    'Product Revenue Concentration',
    top_20_product_revenue_percentage
FROM product_concentration_summary

UNION ALL

SELECT
    'Seller Revenue Concentration',
    top_10_seller_revenue_percentage
FROM seller_concentration_summary;


-- ============================================================
-- 8. DISPLAY RESULTS
-- ============================================================

SELECT *
FROM sales_intelligence_summary;