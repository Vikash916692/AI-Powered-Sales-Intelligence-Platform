SELECT
    COUNT(*) AS total_marts
FROM information_schema.tables
WHERE table_schema = 'sales_intelligence'
  AND table_name LIKE '%_mart';