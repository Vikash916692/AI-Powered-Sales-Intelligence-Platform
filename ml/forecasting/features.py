"""
Feature extraction pipeline for Time-Series Sales & Demand Forecasting.
Builds autoregressive lag, rolling statistics, calendar seasonality, and trend features.
"""

import logging

import numpy as np
import pandas as pd

from ml.common.db import execute_query

logger = logging.getLogger("ml.forecasting.features")


def extract_daily_sales_series() -> pd.DataFrame:
    """
    Extract daily revenue and order volume time series from agg_daily_sales.
    """
    logger.info("Extracting daily revenue time series from agg_daily_sales...")
    sql = """
        SELECT 
            d.full_date AS order_date,
            SUM(ads.revenue) AS daily_revenue,
            SUM(ads.order_count) AS daily_orders,
            SUM(ads.item_count) AS daily_items,
            AVG(ads.average_order_value) AS avg_order_value
        FROM agg_daily_sales ads
        INNER JOIN dim_date d ON ads.date_key = d.date_key
        GROUP BY d.full_date
        ORDER BY d.full_date ASC;
    """
    df = execute_query(sql)
    df["order_date"] = pd.to_datetime(df["order_date"])
    df = df.set_index("order_date").asfreq("D").fillna(0.0).reset_index()

    # Filter to main operating period (start from 2017-01-01)
    df_filtered = df[df["order_date"] >= "2017-01-01"].reset_index(drop=True)
    return pd.DataFrame(df_filtered)


def engineer_forecasting_features(df_series: pd.DataFrame, target_col: str = "daily_revenue") -> pd.DataFrame:
    """
    Generate lag, rolling window, calendar, and trend features for forecasting.
    """
    df = df_series.copy()
    y = df[target_col]

    # Autoregressive Lags
    for lag in [1, 2, 3, 7, 14, 21, 28, 30]:
        df[f"lag_{lag}"] = y.shift(lag)

    # Rolling Window Averages & Standard Deviations
    df["rolling_mean_7"] = y.shift(1).rolling(window=7, min_periods=1).mean()
    df["rolling_std_7"] = y.shift(1).rolling(window=7, min_periods=1).std().fillna(0.0)
    df["rolling_mean_14"] = y.shift(1).rolling(window=14, min_periods=1).mean()
    df["rolling_mean_30"] = y.shift(1).rolling(window=30, min_periods=1).mean()
    df["rolling_std_30"] = y.shift(1).rolling(window=30, min_periods=1).std().fillna(0.0)

    # Calendar Dynamics
    df["day_of_week"] = df["order_date"].dt.dayofweek
    df["day_of_month"] = df["order_date"].dt.day
    df["month"] = df["order_date"].dt.month
    df["quarter"] = df["order_date"].dt.quarter
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)

    # Trend Index
    df["trend_index"] = np.arange(len(df))

    # Black Friday Spike indicator (late November)
    df["is_black_friday_season"] = (
        (df["month"] == 11) & (df["day_of_month"] >= 20) & (df["day_of_month"] <= 30)
    ).astype(int)

    df = df.dropna().reset_index(drop=True)
    return df
