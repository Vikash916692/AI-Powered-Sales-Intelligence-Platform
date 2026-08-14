USE sales_intelligence;

-- ============================================================
-- PHASE 2 - STEP 2.9
-- RFM CUSTOMER SEGMENTATION
-- ============================================================

DROP TABLE IF EXISTS customer_rfm;


-- ============================================================
-- 1. BUILD CUSTOMER RFM SCORES
-- ============================================================

CREATE TABLE customer_rfm AS

WITH customer_summary AS (

    SELECT
        customer_key,

        MAX(purchase_timestamp) AS last_purchase_date,

        COUNT(DISTINCT order_id) AS frequency,

        SUM(price) AS monetary_value

    FROM fact_sales

    GROUP BY customer_key
),

reference_date AS (

    SELECT
        MAX(purchase_timestamp) AS max_purchase_date

    FROM fact_sales
),

rfm_base AS (

    SELECT
        c.customer_key,

        DATEDIFF(
            r.max_purchase_date,
            c.last_purchase_date
        ) AS recency,

        c.frequency,

        ROUND(c.monetary_value, 2) AS monetary_value

    FROM customer_summary c

    CROSS JOIN reference_date r
),

rfm_scores AS (

    SELECT
        customer_key,
        recency,
        frequency,
        monetary_value,

        -- Lower number of days = more recent = higher score
        NTILE(5) OVER (
            ORDER BY recency ASC
        ) AS recency_score,

        -- Higher frequency = higher score
        NTILE(5) OVER (
            ORDER BY frequency ASC
        ) AS frequency_score,

        -- Higher monetary value = higher score
        NTILE(5) OVER (
            ORDER BY monetary_value ASC
        ) AS monetary_score

    FROM rfm_base
)


-- ============================================================
-- 2. CREATE FINAL RFM TABLE INCLUDING SEGMENT
-- ============================================================

SELECT
    customer_key,

    recency,

    frequency,

    monetary_value,

    recency_score,

    frequency_score,

    monetary_score,

    CASE

        WHEN recency_score >= 4
             AND frequency_score >= 4
             AND monetary_score >= 4
        THEN 'Champions'

        WHEN frequency_score >= 4
             AND monetary_score >= 3
        THEN 'Loyal Customers'

        WHEN recency_score >= 4
             AND frequency_score >= 2
        THEN 'Potential Loyalists'

        WHEN recency_score >= 4
             AND frequency_score <= 2
        THEN 'New Customers'

        WHEN recency_score <= 2
             AND frequency_score >= 3
             AND monetary_score >= 3
        THEN 'At Risk'

        WHEN recency_score <= 2
             AND monetary_score >= 4
        THEN 'Cannot Lose Them'

        WHEN recency_score <= 2
        THEN 'Lost Customers'

        ELSE 'Other'

    END AS rfm_segment

FROM rfm_scores;


-- ============================================================
-- 3. CHECK TABLE
-- ============================================================

SELECT
    COUNT(*) AS total_customers,
    COUNT(DISTINCT customer_key) AS unique_customers,
    COUNT(rfm_segment) AS segmented_customers
FROM customer_rfm;


-- ============================================================
-- 4. RFM SEGMENT SUMMARY
-- ============================================================

SELECT
    rfm_segment,

    COUNT(*) AS customers,

    ROUND(AVG(recency), 2) AS avg_recency,

    ROUND(AVG(frequency), 2) AS avg_frequency,

    ROUND(AVG(monetary_value), 2) AS avg_monetary_value

FROM customer_rfm

GROUP BY rfm_segment

ORDER BY customers DESC;