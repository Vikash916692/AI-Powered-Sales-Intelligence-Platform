"""
Inference pipeline for Delivery Delay & Logistics SLA Prediction.
Scores incoming shipment delay probability and assigns delivery risk tiers.
"""

import json
import logging
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import joblib
import pandas as pd

from ml.delivery_delay.features import (
    DELIVERY_CATEGORICAL_COLUMNS,
    DELIVERY_FEATURE_COLUMNS,
    extract_delivery_delay_dataset,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("ml.delivery_delay.predict")

MODELS_DIR = Path(__file__).resolve().parent / "models"


def get_delay_risk_tier(prob: float) -> str:
    """
    Categorize delay probability into logistics operational tier.
    """
    if prob < 0.20:
        return "Low Risk (On-Time Guaranteed)"
    elif prob < 0.50:
        return "Medium Risk (Standard Monitoring)"
    elif prob < 0.75:
        return "High Risk (Expedited Priority)"
    else:
        return "Critical Risk (Proactive SLA Alert)"


class DeliveryDelayPredictor:
    """
    Production Delivery Delay & Logistics SLA Predictor.
    """

    def __init__(self, model_dir: str | Path | None = None):
        self.model_dir = Path(model_dir) if model_dir else MODELS_DIR
        self.model_path = self.model_dir / "model.joblib"
        self.preprocessor_path = self.model_dir / "preprocessing.joblib"
        self.metadata_path = self.model_dir / "metadata.json"

        if not self.model_path.exists() or not self.preprocessor_path.exists():
            raise FileNotFoundError(
                f"Delivery delay model artifacts not found at {self.model_dir}. Please run train.py first."
            )

        self.model = joblib.load(self.model_path)
        self.preprocessor = joblib.load(self.preprocessor_path)

        with open(self.metadata_path, encoding="utf-8") as f:
            self.metadata = json.load(f)

    def predict(self, df_features: pd.DataFrame) -> pd.DataFrame:
        feature_cols = DELIVERY_FEATURE_COLUMNS + DELIVERY_CATEGORICAL_COLUMNS
        missing = [c for c in feature_cols if c not in df_features.columns]
        if missing:
            raise ValueError(f"Missing required features for delivery delay prediction: {missing}")

        X_proc = self.preprocessor.transform(df_features[feature_cols])
        probs = self.model.predict_proba(X_proc)[:, 1]

        results = pd.DataFrame()
        if "order_id" in df_features.columns:
            results["order_id"] = df_features["order_id"]
        if "order_item_id" in df_features.columns:
            results["order_item_id"] = df_features["order_item_id"]

        results["delay_probability"] = [round(float(p), 4) for p in probs]
        results["is_delay_predicted"] = [int(p >= 0.50) for p in probs]
        results["logistics_risk_tier"] = [get_delay_risk_tier(p) for p in probs]
        return results

    def predict_sample(self, limit: int = 10) -> pd.DataFrame:
        df = extract_delivery_delay_dataset()
        sample = df.tail(limit).copy()
        return self.predict(sample)


def predict_sample_demo():
    predictor = DeliveryDelayPredictor()
    scores = predictor.predict_sample(limit=10)
    print("\n" + "=" * 75)
    print("DELIVERY DELAY & LOGISTICS SLA PREDICTION SAMPLE OUTPUT")
    print("=" * 75)
    print(scores.to_string(index=False))
    print("=" * 75)
    return scores


if __name__ == "__main__":
    predict_sample_demo()
