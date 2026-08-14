USE sales_intelligence;

-- ============================================================
-- PHASE 2 - STEP 2.7
-- DELIVERY ANALYTICS
-- ============================================================


-- ------------------------------------------------------------
-- DELIVERY KPIs
-- ------------------------------------------------------------

UPDATE kpi_summary
SET kpi_value = (
    SELECT COALESCE(
        AVG(delivery_days),
        0
    )
    FROM fact_sales
    WHERE delivered_date IS NOT NULL
      AND delivery_days IS NOT NULL
)
WHERE kpi_name = 'average_delivery_time';


UPDATE kpi_summary
SET kpi_value = (
    SELECT
        CASE
            WHEN COUNT(*) = 0 THEN 0
            ELSE
                100.0 *
                SUM(
                    CASE
                        WHEN is_delayed = 1 THEN 1
                        ELSE 0
                    END
                ) / COUNT(*)
        END
    FROM fact_sales
    WHERE delivered_date IS NOT NULL
)
WHERE kpi_name = 'late_delivery_rate';


-- ------------------------------------------------------------
-- DELIVERY PERFORMANCE
-- ------------------------------------------------------------

DROP TABLE IF EXISTS delivery_performance;

CREATE TABLE delivery_performance AS
SELECT
    order_status,

    COUNT(DISTINCT order_id) AS total_orders,

    COUNT(
        DISTINCT CASE
            WHEN delivered_date IS NOT NULL
            THEN order_id
        END
    ) AS delivered_orders,

    ROUND(
        AVG(
            CASE
                WHEN delivered_date IS NOT NULL
                THEN delivery_days
            END
        ),
        2
    ) AS average_delivery_days,

    ROUND(
        AVG(
            CASE
                WHEN delivered_date IS NOT NULL
                THEN delivery_delay_days
            END
        ),
        2
    ) AS average_delivery_delay_days,

    SUM(
        CASE
            WHEN is_delayed = 1 THEN 1
            ELSE 0
        END
    ) AS delayed_items

FROM fact_sales

GROUP BY order_status;


SELECT *
FROM delivery_performance
ORDER BY total_orders DESC;