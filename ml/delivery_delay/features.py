"""
Feature extraction pipeline for Delivery Delay & Logistics SLA Prediction.
Extracts order-level shipment attributes, freight logistics, route geography, and seller reliability.
"""

import logging

import pandas as pd

from ml.common.db import execute_query

logger = logging.getLogger("ml.delivery_delay.features")

DELIVERY_FEATURE_COLUMNS = [
    "price",
    "freight_value",
    "freight_ratio",
    "product_weight_g",
    "product_volume_cm3",
    "estimated_delivery_days",
    "is_interstate",
    "purchase_dayofweek",
    "purchase_month",
    "seller_historical_orders",
    "seller_avg_order_value",
]

DELIVERY_CATEGORICAL_COLUMNS = [
    "customer_state",
    "seller_state",
    "category_name_english",
]


def extract_delivery_delay_dataset() -> pd.DataFrame:
    """
    Extract shipment level dataset for delivery delay classification.
    Target: is_delayed (1 if actual_delivery > estimated_delivery, else 0).
    """
    logger.info("Extracting delivery delay dataset from fact_sales and analytical dimensions...")
    sql = """
        SELECT 
            fs.order_id,
            fs.order_item_id,
            fs.purchase_timestamp,
            fs.price,
            fs.freight_value,
            ROUND(fs.freight_value / (fs.price + 1e-5), 4) AS freight_ratio,
            COALESCE(dp.product_weight_g, 500) AS product_weight_g,
            COALESCE(dp.product_length_cm * dp.product_height_cm * dp.product_width_cm, 1000) AS product_volume_cm3,
            COALESCE(dp.category_name_english, 'other') AS category_name_english,
            c.customer_state,
            s.seller_state,
            CASE WHEN c.customer_state != s.seller_state THEN 1 ELSE 0 END AS is_interstate,
            DATEDIFF(fs.estimated_delivery_date, fs.purchase_timestamp) AS estimated_delivery_days,
            DAYOFWEEK(fs.purchase_timestamp) AS purchase_dayofweek,
            MONTH(fs.purchase_timestamp) AS purchase_month,
            
            -- Seller historical reliability profile
            COALESCE(sm.total_orders, 10) AS seller_historical_orders,
            COALESCE(sm.average_order_value, 100.0) AS seller_avg_order_value,
            
            -- Ground truth target
            fs.is_delayed AS is_delayed,
            COALESCE(fs.delivery_delay_days, 0) AS delivery_delay_days
            
        FROM fact_sales fs
        INNER JOIN dim_customer c ON fs.customer_key = c.customer_key
        INNER JOIN dim_seller s ON fs.seller_key = s.seller_key
        LEFT JOIN dim_product dp ON fs.product_key = dp.product_key
        LEFT JOIN seller_mart sm ON s.seller_key = sm.seller_key
        WHERE fs.order_status = 'delivered'
          AND fs.is_delayed IS NOT NULL;
    """
    df = execute_query(sql)
    df["purchase_timestamp"] = pd.to_datetime(df["purchase_timestamp"])
    df["estimated_delivery_days"] = df["estimated_delivery_days"].fillna(15).clip(lower=1, upper=90)
    df["seller_historical_orders"] = df["seller_historical_orders"].fillna(10)
    df["seller_avg_order_value"] = df["seller_avg_order_value"].fillna(100.0)

    logger.info(
        f"Delivery Delay dataset extracted: {len(df):,} shipment records. "
        f"Delayed Orders: {(df['is_delayed'] == 1).sum():,} ({df['is_delayed'].mean()*100:.2f}%)"
    )
    return df
