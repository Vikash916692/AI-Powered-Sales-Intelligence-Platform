"""
Training pipeline for Delivery Delay & Logistics SLA Prediction.
Trains a high-accuracy classifier predicting shipment delay risk and logistics operational tiers.
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
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.inspection import permutation_importance
from sklearn.metrics import classification_report

from ml.common.evaluation import evaluate_classification
from ml.common.preprocessing import RobustPreprocessor
from ml.delivery_delay.features import (
    DELIVERY_CATEGORICAL_COLUMNS,
    DELIVERY_FEATURE_COLUMNS,
    extract_delivery_delay_dataset,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("ml.delivery_delay.train")

MODELS_DIR = Path(__file__).resolve().parent / "models"


def train_delivery_delay_model() -> dict:
    """
    Train and evaluate the delivery delay prediction model.
    """
    logger.info("==================================================")
    logger.info("STARTING DELIVERY DELAY MODEL TRAINING PIPELINE")
    logger.info("==================================================")
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    df = extract_delivery_delay_dataset()

    # Chronological Split
    df = df.sort_values("purchase_timestamp").reset_index(drop=True)
    n = len(df)
    train_idx = int(n * 0.70)

    train_df = df.iloc[:train_idx]
    test_df = df.iloc[train_idx:]

    logger.info(f"Partitions: Train={len(train_df):,}, Test={len(test_df):,}")

    feature_cols = DELIVERY_FEATURE_COLUMNS + DELIVERY_CATEGORICAL_COLUMNS
    X_train_raw = train_df[feature_cols]
    y_train = train_df["is_delayed"].values

    X_test_raw = test_df[feature_cols]
    y_test = test_df["is_delayed"].values

    # Preprocessing
    preprocessor = RobustPreprocessor(
        numeric_features=DELIVERY_FEATURE_COLUMNS,
        categorical_features=DELIVERY_CATEGORICAL_COLUMNS,
        scaler_type="robust",
    )
    X_train = preprocessor.fit_transform(X_train_raw)
    X_test = preprocessor.transform(X_test_raw)

    # Model Training
    logger.info("Training HistGradientBoostingClassifier with balanced weights...")
    model = HistGradientBoostingClassifier(
        max_iter=200,
        max_depth=6,
        min_samples_leaf=20,
        learning_rate=0.08,
        class_weight="balanced",
        random_state=42,
    )
    model.fit(X_train, y_train)

    # Evaluation on Hold-Out Test Set
    test_probs = model.predict_proba(X_test)[:, 1]
    test_preds = (test_probs >= 0.50).astype(int)

    test_metrics = evaluate_classification(y_test, test_preds, test_probs)
    report = classification_report(y_test, test_preds, output_dict=True)

    logger.info(f"Test Set Evaluation: {json.dumps(test_metrics, indent=2)}")

    # Permutation Feature Importance
    logger.info("Computing feature importances...")
    perm = permutation_importance(model, X_test, y_test, scoring="roc_auc", n_repeats=3, random_state=42)
    feat_names = list(preprocessor.numeric_features) + list(preprocessor.cat_encoder.get_feature_names_out(preprocessor.categorical_features))
    means = perm["importances_mean"] if isinstance(perm, dict) else perm.importances_mean
    importances = {feat_names[i]: round(float(means[i]), 5) for i in range(min(len(feat_names), len(means)))}
    top_importances = dict(sorted(importances.items(), key=lambda x: x[1], reverse=True)[:15])

    # Save Artifacts
    joblib.dump(model, MODELS_DIR / "model.joblib")
    joblib.dump(preprocessor, MODELS_DIR / "preprocessing.joblib")

    metrics_payload = {
        "test_metrics": test_metrics,
        "classification_report": report,
        "test_row_count": len(test_df),
        "test_delayed_count": int(y_test.sum()),
        "top_features": top_importances,
    }
    with open(MODELS_DIR / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics_payload, f, indent=4)

    metadata_payload = {
        "model_name": "Delivery Delay & Logistics SLA Predictor",
        "target": "is_delayed",
        "total_records": len(df),
        "train_rows": len(train_df),
        "test_rows": len(test_df),
        "feature_count": len(feature_cols),
        "numeric_features": DELIVERY_FEATURE_COLUMNS,
        "categorical_features": DELIVERY_CATEGORICAL_COLUMNS,
        "evaluation_summary": test_metrics,
        "created_at": datetime.now(UTC).isoformat(),
    }
    with open(MODELS_DIR / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata_payload, f, indent=4)

    logger.info("Delivery Delay Model training and serialization complete.")
    return metrics_payload


if __name__ == "__main__":
    train_delivery_delay_model()
