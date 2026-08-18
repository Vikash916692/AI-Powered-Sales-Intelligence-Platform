"""
Inference pipeline for Customer Review Sentiment & Complaint NLP.
Scores raw Portuguese review messages and assigns sentiment polarity and support ticket priorities.
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

from ml.review_sentiment.features import clean_portuguese_text

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("ml.review_sentiment.predict")

MODELS_DIR = Path(__file__).resolve().parent / "models"


def get_sentiment_tier(prob_complaint: float) -> str:
    """
    Map complaint probability to sentiment tier and CRM action priority.
    """
    if prob_complaint >= 0.70:
        return "Critical Complaint (Urgent Support Intervention)"
    elif prob_complaint >= 0.40:
        return "Mild Dissatisfaction (Standard Follow-up)"
    else:
        return "Positive / Satisfied Customer"


class ReviewSentimentPredictor:
    """
    Production Customer Review Sentiment & Complaint NLP Classifier.
    """

    def __init__(self, model_dir: str | Path | None = None):
        self.model_dir = Path(model_dir) if model_dir else MODELS_DIR
        self.model_path = self.model_dir / "model.joblib"
        self.vectorizer_path = self.model_dir / "vectorizer.joblib"
        self.metadata_path = self.model_dir / "metadata.json"

        if not self.model_path.exists() or not self.vectorizer_path.exists():
            raise FileNotFoundError(
                f"Review Sentiment artifacts not found at {self.model_dir}. Please run train.py first."
            )

        self.model = joblib.load(self.model_path)
        self.vectorizer = joblib.load(self.vectorizer_path)

        with open(self.metadata_path, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)

    def predict_text(self, text_list: list[str]) -> pd.DataFrame:
        """
        Score a list of raw Portuguese review strings.
        """
        cleaned = [clean_portuguese_text(t) for t in text_list]
        X_vec = self.vectorizer.transform(cleaned)
        probs = self.model.predict_proba(X_vec)[:, 1]

        results = []
        for raw_t, p in zip(text_list, probs, strict=False):
            results.append({
                "review_text": raw_t[:80] + ("..." if len(raw_t) > 80 else ""),
                "complaint_probability": round(float(p), 4),
                "is_complaint_predicted": int(p >= 0.50),
                "sentiment_tier": get_sentiment_tier(p),
            })
        return pd.DataFrame(results)


def predict_sample_demo():
    predictor = ReviewSentimentPredictor()
    sample_texts = [
        "Produto excelente, chegou antes do prazo e muito bem embalado! Recomendo.",
        "Não recebi o produto, faz mais de um mês de atraso e o vendedor não responde!",
        "O produto veio quebrado na caixa e com defeito de fábrica. Quero meu dinheiro de volta.",
        "Tudo certo, produto conforme a descrição.",
    ]
    scores = predictor.predict_text(sample_texts)
    print("\n" + "=" * 80)
    print("CUSTOMER REVIEW SENTIMENT & COMPLAINT NLP SAMPLE PREDICTIONS")
    print("=" * 80)
    print(scores.to_string(index=False))
    print("=" * 80)
    return scores


if __name__ == "__main__":
    predict_sample_demo()
