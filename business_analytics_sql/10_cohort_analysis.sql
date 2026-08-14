USE sales_intelligence;

-- ============================================================
-- PHASE 2 - STEP 2.10
-- CUSTOMER COHORT ANALYSIS
-- ============================================================

DROP TABLE IF EXISTS customer_cohort;

DROP TABLE IF EXISTS cohort_retention;


-- ============================================================
-- 1. IDENTIFY EACH CUSTOMER'S FIRST PURCHASE
-- ============================================================

CREATE TABLE customer_cohort AS

WITH first_purchase AS (

    SELECT
        customer_key,

        MIN(purchase_timestamp) AS first_purchase_timestamp

    FROM fact_sales

    GROUP BY customer_key
),

customer_activity AS (

    SELECT DISTINCT

        f.customer_key,

        fp.first_purchase_timestamp,

        DATE_FORMAT(
            fp.first_purchase_timestamp,
            '%Y-%m-01'
        ) AS cohort_month,

        DATE_FORMAT(
            f.purchase_timestamp,
            '%Y-%m-01'
        ) AS activity_month

    FROM fact_sales f

    INNER JOIN first_purchase fp
        ON f.customer_key = fp.customer_key
)

SELECT

    customer_key,

    first_purchase_timestamp,

    STR_TO_DATE(
        cohort_month,
        '%Y-%m-%d'
    ) AS cohort_month,

    STR_TO_DATE(
        activity_month,
        '%Y-%m-%d'
    ) AS activity_month,

    TIMESTAMPDIFF(
        MONTH,
        STR_TO_DATE(cohort_month, '%Y-%m-%d'),
        STR_TO_DATE(activity_month, '%Y-%m-%d')
    ) AS cohort_month_number

FROM customer_activity;


-- ============================================================
-- 2. COHORT RETENTION COUNTS
-- ============================================================

CREATE TABLE cohort_retention AS

SELECT

    cohort_month,

    cohort_month_number,

    COUNT(DISTINCT customer_key) AS active_customers

FROM customer_cohort

GROUP BY
    cohort_month,
    cohort_month_number;


-- ============================================================
-- 3. COHORT SIZE
-- ============================================================

DROP TABLE IF EXISTS cohort_size;

CREATE TABLE cohort_size AS

SELECT

    cohort_month,

    COUNT(DISTINCT customer_key) AS cohort_customers

FROM customer_cohort

WHERE cohort_month_number = 0

GROUP BY cohort_month;


-- ============================================================
-- 4. COHORT RETENTION PERCENTAGE
-- ============================================================

DROP TABLE IF EXISTS cohort_retention_rate;

CREATE TABLE cohort_retention_rate AS

SELECT

    cr.cohort_month,

    cr.cohort_month_number,

    cr.active_customers,

    cs.cohort_customers,

    ROUND(
        100.0 * cr.active_customers
        / NULLIF(cs.cohort_customers, 0),
        2
    ) AS retention_rate

FROM cohort_retention cr

INNER JOIN cohort_size cs
    ON cr.cohort_month = cs.cohort_month;


-- ============================================================
-- 5. BASIC VALIDATION
-- ============================================================

SELECT
    COUNT(DISTINCT customer_key) AS total_customers
FROM customer_cohort;


SELECT
    COUNT(*) AS cohort_rows,
    COUNT(DISTINCT cohort_month) AS cohorts
FROM cohort_retention_rate;


-- ============================================================
-- 6. DISPLAY COHORT RETENTION
-- ============================================================

SELECT

    cohort_month,

    cohort_month_number,

    active_customers,

    cohort_customers,

    retention_rate

FROM cohort_retention_rate

ORDER BY
    cohort_month,
    cohort_month_number;