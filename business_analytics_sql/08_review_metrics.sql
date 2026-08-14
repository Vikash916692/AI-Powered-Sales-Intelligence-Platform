USE sales_intelligence;

-- ============================================================
-- PHASE 2 - STEP 2.8
-- CUSTOMER REVIEW ANALYTICS
-- ============================================================


-- ------------------------------------------------------------
-- REVIEW KPIs
-- ------------------------------------------------------------

UPDATE kpi_summary
SET kpi_value = (
    SELECT COALESCE(
        AVG(review_score),
        0
    )
    FROM fact_reviews
)
WHERE kpi_name = 'average_review_score';


UPDATE kpi_summary
SET kpi_value = (
    SELECT
        CASE
            WHEN COUNT(*) = 0 THEN 0
            ELSE
                100.0 *
                SUM(
                    CASE
                        WHEN review_score >= 4 THEN 1
                        ELSE 0
                    END
                ) / COUNT(*)
        END
    FROM fact_reviews
)
WHERE kpi_name = 'positive_review_rate';


UPDATE kpi_summary
SET kpi_value = (
    SELECT
        CASE
            WHEN COUNT(*) = 0 THEN 0
            ELSE
                100.0 *
                SUM(
                    CASE
                        WHEN review_score <= 2 THEN 1
                        ELSE 0
                    END
                ) / COUNT(*)
        END
    FROM fact_reviews
)
WHERE kpi_name = 'negative_review_rate';


-- ------------------------------------------------------------
-- REVIEW DISTRIBUTION
-- ------------------------------------------------------------

DROP TABLE IF EXISTS review_distribution;

CREATE TABLE review_distribution AS
SELECT
    review_score,

    COUNT(*) AS review_count,

    ROUND(
        100.0 * COUNT(*) /
        NULLIF(
            (SELECT COUNT(*) FROM fact_reviews),
            0
        ),
        2
    ) AS percentage_of_reviews

FROM fact_reviews

GROUP BY review_score;


SELECT *
FROM review_distribution
ORDER BY review_score;