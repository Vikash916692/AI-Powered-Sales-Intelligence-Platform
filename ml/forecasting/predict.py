"""
Inference pipeline for Multi-Horizon Sales & Demand Forecasting.
Generates multi-step recursive forward revenue forecasts with confidence intervals.
"""

import json
import logging
import sys
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import joblib
import numpy as np
import pandas as pd

from ml.forecasting.features import (
    engineer_forecasting_features,
    extract_daily_sales_series,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("ml.forecasting.predict")

MODELS_DIR = Path(__file__).resolve().parent / "models"


class SalesForecaster:
    """
    Production Multi-Step Sales & Demand Forecaster.
    """

    def __init__(self, model_dir: str | Path | None = None):
        self.model_dir = Path(model_dir) if model_dir else MODELS_DIR
        self.model_path = self.model_dir / "model.joblib"
        self.preprocessor_path = self.model_dir / "preprocessing.joblib"
        self.metadata_path = self.model_dir / "metadata.json"
        self.metrics_path = self.model_dir / "metrics.json"

        if not self.model_path.exists() or not self.preprocessor_path.exists():
            raise FileNotFoundError(
                f"Forecasting model artifacts not found at {self.model_dir}. Please run train.py first."
            )

        self.model = joblib.load(self.model_path)
        self.preprocessor = joblib.load(self.preprocessor_path)

        with open(self.metadata_path, encoding="utf-8") as f:
            self.metadata = json.load(f)

        with open(self.metrics_path, encoding="utf-8") as f:
            metrics = json.load(f)
            self.residual_std = metrics.get("residual_std", 3500.0)

    def forecast_future(self, horizon_days: int = 30) -> pd.DataFrame:
        """
        Generate recursive multi-step future sales forecast for `horizon_days` ahead.
        """
        logger.info(f"Generating forward {horizon_days}-day sales demand forecast...")
        history_df = extract_daily_sales_series()

        current_series = pd.DataFrame(history_df[["order_date", "daily_revenue"]].copy())
        last_date = current_series["order_date"].max()

        future_records = []

        for step in range(1, horizon_days + 1):
            next_date = last_date + timedelta(days=step)

            # Engineer features from current state
            feat_df = engineer_forecasting_features(current_series, target_col="daily_revenue")
            latest_row = feat_df.tail(1).copy()
            latest_row["order_date"] = next_date

            # Update calendar attributes for the forecast date
            latest_row["day_of_week"] = next_date.dayofweek
            latest_row["day_of_month"] = next_date.day
            latest_row["month"] = next_date.month
            latest_row["quarter"] = next_date.quarter
            latest_row["is_weekend"] = int(next_date.dayofweek >= 5)
            latest_row["trend_index"] = len(current_series)
            latest_row["is_black_friday_season"] = int((next_date.month == 11) and (20 <= next_date.day <= 30))

            feature_cols = self.metadata["feature_list"]
            X_proc = self.preprocessor.transform(latest_row[feature_cols])

            pred_rev = float(np.clip(self.model.predict(X_proc)[0], 0.0, None))

            # Prediction intervals (1.96 std for 95% confidence bounds)
            uncertainty = 1.96 * self.residual_std * np.sqrt(1 + (step * 0.02))
            lower_bound = max(0.0, pred_rev - uncertainty)
            upper_bound = pred_rev + uncertainty

            future_records.append({
                "forecast_date": next_date.strftime("%Y-%m-%d"),
                "yhat": round(pred_rev, 2),
                "yhat_lower": round(lower_bound, 2),
                "yhat_upper": round(upper_bound, 2),
            })

            # Append prediction to series for next recursive lag step
            new_row = pd.DataFrame([{"order_date": next_date, "daily_revenue": pred_rev}])
            current_series = pd.concat([current_series, new_row], ignore_index=True)

        return pd.DataFrame(future_records)


def forecast_sample_demo():
    forecaster = SalesForecaster()
    forecast = forecaster.forecast_future(horizon_days=10)
    print("\n" + "=" * 65)
    print("SALES & DEMAND FORWARD FORECAST SAMPLE OUTPUT (10 DAYS)")
    print("=" * 65)
    print(forecast.to_string(index=False))
    print("=" * 65)
    return forecast


if __name__ == "__main__":
    forecast_sample_demo()
