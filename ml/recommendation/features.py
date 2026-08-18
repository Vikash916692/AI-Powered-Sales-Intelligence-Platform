"""
Feature extraction pipeline for Product Recommendation & Market Basket Analysis.
Extracts order-product co-occurrence baskets and category affinity matrices.
"""

import logging

import pandas as pd

from ml.common.db import execute_query

logger = logging.getLogger("ml.recommendation.features")


def extract_order_baskets() -> pd.DataFrame:
    """
    Extract order-item transaction pairs for collaborative filtering and association rule mining.
    """
    logger.info("Extracting order-item transaction baskets from fact_sales and dim_product...")
    sql = """
        SELECT 
            fs.order_id,
            dp.product_id,
            COALESCE(dp.category_name_english, 'other') AS category_name_english,
            fs.price
        FROM fact_sales fs
        INNER JOIN dim_product dp ON fs.product_key = dp.product_key
        WHERE fs.order_status = 'delivered';
    """
    df = execute_query(sql)
    logger.info(f"Extracted {len(df):,} item records across {df['order_id'].nunique():,} unique orders.")
    return df
