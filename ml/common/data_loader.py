"""
Validated data loaders for Phase 2 analytical data marts and transaction tables.
"""

import logging

import pandas as pd

from ml.common.db import execute_query

logger = logging.getLogger("ml.common.data_loader")


class DataLoader:
    """
    Unified schema-validated loader for Phase 2 data marts.
    """

    @staticmethod
    def load_customer_mart() -> pd.DataFrame:
        logger.info("Loading customer_mart...")
        return execute_query("SELECT * FROM customer_mart;")

    @staticmethod
    def load_product_mart() -> pd.DataFrame:
        logger.info("Loading product_mart...")
        return execute_query("SELECT * FROM product_mart;")

    @staticmethod
    def load_seller_mart() -> pd.DataFrame:
        logger.info("Loading seller_mart...")
        return execute_query("SELECT * FROM seller_mart;")

    @staticmethod
    def load_daily_sales_mart() -> pd.DataFrame:
        logger.info("Loading daily_sales_mart...")
        return execute_query("SELECT * FROM daily_sales_mart ORDER BY date_key ASC;")

    @staticmethod
    def load_order_fulfillment_mart() -> pd.DataFrame:
        logger.info("Loading order_fulfillment_mart...")
        return execute_query("SELECT * FROM order_fulfillment_mart;")

    @staticmethod
    def load_fact_sales() -> pd.DataFrame:
        logger.info("Loading fact_sales transactions...")
        return execute_query("SELECT * FROM fact_sales;")

    @staticmethod
    def load_fact_reviews() -> pd.DataFrame:
        logger.info("Loading fact_reviews...")
        return execute_query("SELECT * FROM fact_reviews;")
