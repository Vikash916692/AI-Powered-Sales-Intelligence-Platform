USE sales_intelligence;

-- ============================================================
-- PHASE 2 - STEP 2.2
-- CORE SALES METRICS
-- ============================================================


-- ============================================================
-- 1. CALCULATE CORE SALES KPIs
-- ============================================================

UPDATE kpi_summary
SET kpi_value = (
    SELECT COALESCE(SUM(price), 0)
    FROM fact_sales
)
WHERE kpi_name = 'total_revenue';


UPDATE kpi_summary
SET kpi_value = (
    SELECT COALESCE(SUM(freight_value), 0)
    FROM fact_sales
)
WHERE kpi_name = 'total_freight';


UPDATE kpi_summary
SET kpi_value = (
    SELECT COALESCE(SUM(total_item_value), 0)
    FROM fact_sales
)
WHERE kpi_name = 'total_sales_value';


UPDATE kpi_summary
SET kpi_value = (
    SELECT COUNT(DISTINCT order_id)
    FROM fact_sales
)
WHERE kpi_name = 'total_orders';


UPDATE kpi_summary
SET kpi_value = (
    SELECT
        CASE
            WHEN COUNT(DISTINCT order_id) = 0 THEN 0
            ELSE SUM(price) / COUNT(DISTINCT order_id)
        END
    FROM fact_sales
)
WHERE kpi_name = 'average_order_value';


UPDATE kpi_summary
SET kpi_value = (
    SELECT
        CASE
            WHEN COUNT(*) = 0 THEN 0
            ELSE SUM(price) / COUNT(*)
        END
    FROM fact_sales
)
WHERE kpi_name = 'average_item_value';


-- ============================================================
-- 2. DISPLAY THE CALCULATED KPIs
-- ============================================================

SELECT
    kpi_id,
    kpi_name,
    kpi_category,
    ROUND(kpi_value, 2) AS kpi_value,
    last_updated
FROM kpi_summary
WHERE kpi_category = 'Sales'
ORDER BY kpi_id;