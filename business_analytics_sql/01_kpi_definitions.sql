USE sales_intelligence;

-- ============================================================
-- PHASE 2 - KPI DEFINITIONS
-- AI POWERED SALES INTELLIGENCE
-- ============================================================

-- ------------------------------------------------------------
-- CORE SALES KPIs
-- ------------------------------------------------------------

-- Total number of unique orders
-- Grain: order
-- Source: fact_sales
-- ------------------------------------------------------------

-- Total Revenue / GMV
-- Revenue generated from product prices
-- ------------------------------------------------------------

-- Total Freight
-- Total freight charges associated with order items
-- ------------------------------------------------------------

-- Total Sales Value
-- Product price + freight
-- ------------------------------------------------------------

-- Average Order Value (AOV)
-- Total product revenue / unique orders
-- ------------------------------------------------------------

-- Average Item Value
-- Total product revenue / number of order items
-- ------------------------------------------------------------


-- ------------------------------------------------------------
-- CUSTOMER KPIs
-- ------------------------------------------------------------

-- Total Customers
-- Number of unique customers who placed orders
-- ------------------------------------------------------------

-- New Customers
-- Customers making their first purchase in the selected period
-- ------------------------------------------------------------

-- Repeat Customers
-- Customers with more than one order
-- ------------------------------------------------------------

-- Repeat Customer Rate
-- Repeat customers / total customers
-- ------------------------------------------------------------


-- ------------------------------------------------------------
-- PRODUCT KPIs
-- ------------------------------------------------------------

-- Total Products Sold
-- Number of order items
-- ------------------------------------------------------------

-- Unique Products Sold
-- Number of distinct products appearing in sales
-- ------------------------------------------------------------

-- Average Product Price
-- Average item price
-- ------------------------------------------------------------


-- ------------------------------------------------------------
-- SELLER KPIs
-- ------------------------------------------------------------

-- Total Sellers
-- Number of unique sellers generating sales
-- ------------------------------------------------------------

-- Average Revenue per Seller
-- Total revenue / active sellers
-- ------------------------------------------------------------


-- ------------------------------------------------------------
-- REVIEW KPIs
-- ------------------------------------------------------------

-- Average Review Score
-- Average score across reviews
-- ------------------------------------------------------------

-- Positive Review Rate
-- Percentage of reviews with score >= 4
-- ------------------------------------------------------------

-- Negative Review Rate
-- Percentage of reviews with score <= 2
-- ------------------------------------------------------------


-- ------------------------------------------------------------
-- DELIVERY KPIs
-- ------------------------------------------------------------

-- Average Delivery Time
-- Actual delivery date - purchase date
-- ------------------------------------------------------------

-- Late Delivery Rate
-- Orders delivered after estimated delivery date
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS kpi_summary (
    kpi_id INT AUTO_INCREMENT PRIMARY KEY,
    kpi_name VARCHAR(100) NOT NULL UNIQUE,
    kpi_category VARCHAR(50) NOT NULL,
    kpi_description TEXT,
    kpi_value DECIMAL(20,4),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP
);

INSERT INTO kpi_summary
    (kpi_name, kpi_category, kpi_description)
VALUES
    (
        'total_revenue',
        'Sales',
        'Total product revenue generated from sales'
    ),
    (
        'total_freight',
        'Sales',
        'Total freight charges associated with sold items'
    ),
    (
        'total_sales_value',
        'Sales',
        'Product revenue plus freight charges'
    ),
    (
        'total_orders',
        'Sales',
        'Number of unique orders'
    ),
    (
        'average_order_value',
        'Sales',
        'Total product revenue divided by unique orders'
    ),
    (
        'average_item_value',
        'Sales',
        'Total product revenue divided by number of order items'
    ),
    (
        'total_customers',
        'Customer',
        'Number of unique customers generating sales'
    ),
    (
        'new_customers',
        'Customer',
        'Customers making their first purchase in the period'
    ),
    (
        'repeat_customers',
        'Customer',
        'Customers with more than one order'
    ),
    (
        'repeat_customer_rate',
        'Customer',
        'Percentage of customers with more than one order'
    ),
    (
        'total_products_sold',
        'Product',
        'Total number of order items sold'
    ),
    (
        'unique_products_sold',
        'Product',
        'Number of distinct products sold'
    ),
    (
        'average_product_price',
        'Product',
        'Average selling price per order item'
    ),
    (
        'total_sellers',
        'Seller',
        'Number of unique sellers generating sales'
    ),
    (
        'average_revenue_per_seller',
        'Seller',
        'Average product revenue generated per active seller'
    ),
    (
        'average_review_score',
        'Review',
        'Average customer review score'
    ),
    (
        'positive_review_rate',
        'Review',
        'Percentage of reviews with score >= 4'
    ),
    (
        'negative_review_rate',
        'Review',
        'Percentage of reviews with score <= 2'
    ),
    (
        'average_delivery_time',
        'Delivery',
        'Average number of days between purchase and delivery'
    ),
    (
        'late_delivery_rate',
        'Delivery',
        'Percentage of delivered orders arriving after estimated delivery'
    )
ON DUPLICATE KEY UPDATE
    kpi_category = VALUES(kpi_category),
    kpi_description = VALUES(kpi_description);