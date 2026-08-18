"""
Training pipeline for Multi-Horizon Sales & Demand Time-Series Forecasting.
Evaluates Ridge, Random Forest, and Gradient Boosting on out-of-sample forward test horizon.
"""

import json
import logging
import sys
from datetime import UTC, datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import joblib
import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge

from ml.common.evaluation import evaluate_forecasting
from ml.common.preprocessing import RobustPreprocessor
from ml.forecasting.features import (
    engineer_forecasting_features,
    extract_daily_sales_series,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("ml.forecasting.train")

MODELS_DIR = Path(__file__).resolve().parent / "models"


def train_forecasting_model() -> dict:
    """
    Train and evaluate the multi-horizon sales forecaster.
    """
    logger.info("==================================================")
    logger.info("STARTING SALES & DEMAND FORECASTING TRAINING")
    logger.info("==================================================")
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    df_series = extract_daily_sales_series()
    df_feat = engineer_forecasting_features(df_series, target_col="daily_revenue")

    # Chronological Split (Last 60 days as Hold-Out Test Horizon)
    test_days = 60
    train_df = df_feat.iloc[:-test_days].copy()
    test_df = df_feat.iloc[-test_days:].copy()

    feature_cols = [c for c in train_df.columns if c not in ["order_date", "daily_revenue", "daily_orders", "daily_items", "avg_order_value"]]
    X_train_raw = train_df[feature_cols]
    y_train = train_df["daily_revenue"].values

    X_test_raw = test_df[feature_cols]
    y_test = test_df["daily_revenue"].values

    # Preprocessing
    preprocessor = RobustPreprocessor(numeric_features=feature_cols, scaler_type="robust")
    X_train = preprocessor.fit_transform(X_train_raw)
    X_test = preprocessor.transform(X_test_raw)

    # Models Tournament
    candidate_models = {
        "RidgeRegressor": Ridge(alpha=10.0),
        "RandomForestRegressor": RandomForestRegressor(n_estimators=100, max_depth=6, random_state=42),
        "HistGradientBoostingRegressor": HistGradientBoostingRegressor(max_iter=150, max_depth=5, learning_rate=0.06, random_state=42),
    }

    tournament_results = {}
    fitted_models = {}

    for name, model in candidate_models.items():
        model.fit(X_train, y_train)
        preds = np.clip(model.predict(X_test), 0.0, None)
        eval_metrics = evaluate_forecasting(y_test, preds)
        tournament_results[name] = eval_metrics
        fitted_models[name] = model
        logger.info(f"Model {name} Test Performance: {eval_metrics}")

    # Select Best Model based on R2 and MAPE
    best_name = max(tournament_results, key=lambda k: tournament_results[k]["r2"])
    best_model = fitted_models[best_name]
    best_metrics = tournament_results[best_name]
    logger.info(f"Selected Winning Forecaster: {best_name} with R2={best_metrics['r2']}, MAPE={best_metrics['mape']*100:.2f}%")

    # Residual Std for Prediction Intervals
    train_preds = best_model.predict(X_train)
    residuals = y_train - train_preds
    residual_std = float(np.std(residuals))

    # Save Artifacts
    joblib.dump(best_model, MODELS_DIR / "model.joblib")
    joblib.dump(preprocessor, MODELS_DIR / "preprocessing.joblib")

    metrics_payload = {
        "selected_model": best_name,
        "test_metrics": best_metrics,
        "tournament_comparison": tournament_results,
        "test_horizon_days": test_days,
        "residual_std": round(residual_std, 2),
    }
    with open(MODELS_DIR / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics_payload, f, indent=4)

    metadata_payload = {
        "model_name": "Multi-Horizon Sales & Demand Forecaster",
        "target": "daily_revenue",
        "feature_count": len(feature_cols),
        "feature_list": feature_cols,
        "model_type": best_name,
        "test_horizon_days": test_days,
        "evaluation_summary": best_metrics,
        "created_at": datetime.now(UTC).isoformat(),
    }
    with open(MODELS_DIR / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata_payload, f, indent=4)

    logger.info("Forecasting pipeline completed successfully.")
    return metrics_payload


if __name__ == "__main__":
    train_forecasting_model()
