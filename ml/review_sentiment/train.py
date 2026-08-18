"""
Training pipeline for Customer Review Sentiment & Complaint NLP.
Trains a TF-IDF classifier predicting customer sentiment and operational complaints with high accuracy and F1 score.
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
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

from ml.common.evaluation import evaluate_classification
from ml.review_sentiment.features import extract_review_nlp_dataset

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("ml.review_sentiment.train")

MODELS_DIR = Path(__file__).resolve().parent / "models"


def train_sentiment_nlp_model() -> dict:
    """
    Train and evaluate the NLP Review Sentiment and Complaint classifier.
    """
    logger.info("==================================================")
    logger.info("STARTING REVIEW SENTIMENT NLP MODEL TRAINING")
    logger.info("==================================================")
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    df = extract_review_nlp_dataset()

    # Binary Complaint Classification: 1 if Complaint (1-2 stars), 0 if Satisfied (4-5 stars)
    df_binary = df[df["review_score"] != 3].copy()
    X = np.array(df_binary["cleaned_text"].tolist())
    y = np.array(df_binary["is_complaint"].tolist(), dtype=int)

    # Train/Test Split (80/20)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    logger.info(f"Dataset Partitions: Train={len(X_train):,}, Test={len(X_test):,}")

    # Vectorization
    logger.info("Fitting TF-IDF Vectorizer on Portuguese text...")
    vectorizer = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        sublinear_tf=True,
        min_df=3,
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    # Model Training
    logger.info("Training LogisticRegression Complaint Classifier...")
    model = LogisticRegression(C=2.0, max_iter=500, class_weight="balanced", random_state=42)
    model.fit(X_train_vec, y_train)

    # Evaluation
    test_probs = model.predict_proba(X_test_vec)[:, 1]
    test_preds = (test_probs >= 0.50).astype(int)
    y_test_arr = np.asarray(y_test, dtype=int)

    test_metrics = evaluate_classification(y_test_arr, test_preds, test_probs)
    report = classification_report(y_test_arr, test_preds, target_names=["Satisfied", "Complaint"], output_dict=True)

    logger.info(f"Test Set Evaluation: {json.dumps(test_metrics, indent=2)}")

    # Extract Top Predictive Words for Complaints vs Satisfaction
    feature_names = vectorizer.get_feature_names_out()
    coefs = model.coef_[0]
    top_complaint_idx = coefs.argsort()[::-1][:15]
    top_satisfied_idx = coefs.argsort()[:15]

    top_complaint_words = [feature_names[i] for i in top_complaint_idx]
    top_satisfied_words = [feature_names[i] for i in top_satisfied_idx]

    logger.info(f"Top Complaint Trigger Words: {top_complaint_words[:8]}")
    logger.info(f"Top Satisfaction Trigger Words: {top_satisfied_words[:8]}")

    # Save Artifacts
    joblib.dump(model, MODELS_DIR / "model.joblib")
    joblib.dump(vectorizer, MODELS_DIR / "vectorizer.joblib")

    metrics_payload = {
        "test_metrics": test_metrics,
        "classification_report": report,
        "test_row_count": len(X_test),
        "test_complaints_count": int(np.sum(y_test_arr)),
        "top_complaint_words": top_complaint_words,
        "top_satisfied_words": top_satisfied_words,
    }
    with open(MODELS_DIR / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics_payload, f, indent=4)

    metadata_payload = {
        "model_name": "Customer Review Sentiment & Complaint NLP Classifier",
        "target": "is_complaint (1: Dissatisfied 1-2 Stars, 0: Satisfied 4-5 Stars)",
        "vocabulary_size": len(feature_names),
        "total_reviews_trained": len(df_binary),
        "evaluation_summary": test_metrics,
        "created_at": datetime.now(UTC).isoformat(),
    }
    with open(MODELS_DIR / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata_payload, f, indent=4)

    logger.info("Review Sentiment NLP training and serialization complete.")
    return metrics_payload


if __name__ == "__main__":
    train_sentiment_nlp_model()
