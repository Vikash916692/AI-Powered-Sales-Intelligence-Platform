"""
Feature extraction pipeline for Review Sentiment & Customer Complaint NLP.
Cleans raw Portuguese text, tokenizes review messages, and extracts complaint labels.
"""

import logging
import re

import pandas as pd

from ml.common.db import execute_query

logger = logging.getLogger("ml.review_sentiment.features")

PORTUGUESE_STOPWORDS = {
    "a", "ao", "aos", "aquela", "aquelas", "aquele", "aqueles", "aquilo", "as", "através",
    "com", "como", "da", "das", "de", "dela", "delas", "dele", "deles", "do", "dos", "e",
    "ela", "elas", "ele", "eles", "em", "entre", "era", "eram", "eramos", "essa", "essas",
    "esse", "esses", "esta", "estas", "este", "estes", "estou", "eu", "foi", "fomos", "foram",
    "me", "meu", "meus", "minha", "minhas", "muito", "na", "nas", "no", "nos", "nossa",
    "nossas", "nosso", "nossos", "num", "numa", "o", "os", "ou", "para", "pela", "pelas",
    "pelo", "pelos", "por", "que", "se", "seu", "seus", "sua", "suas", "tambem", "te",
    "tem", "temos", "tenho", "teu", "teus", "tu", "tua", "tuas", "um", "uma", "voce", "voces"
}


def clean_portuguese_text(text: str) -> str:
    """
    Clean, lowercase, and remove special characters from Portuguese review text.
    """
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"https?://\S+|www\.\S+", "", text)
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\d+", "", text)
    tokens = [w for w in text.split() if w not in PORTUGUESE_STOPWORDS and len(w) > 2]
    return " ".join(tokens)


def extract_review_nlp_dataset() -> pd.DataFrame:
    """
    Extract reviews with written text comments and map to sentiment classes.
    """
    logger.info("Extracting customer reviews with written comments from fact_reviews...")
    sql = """
        SELECT 
            review_id,
            order_id,
            review_score,
            review_comment_title,
            review_comment_message,
            review_creation_date
        FROM fact_reviews
        WHERE review_comment_message IS NOT NULL
          AND review_comment_message != '';
    """
    df = execute_query(sql)

    # Combine title and message
    df["full_text"] = df["review_comment_title"].fillna("") + " " + df["review_comment_message"].fillna("")
    df["cleaned_text"] = df["full_text"].apply(clean_portuguese_text)

    # Map sentiment class: 1-2 = Negative (0), 3 = Neutral (1), 4-5 = Positive (2)
    def map_sentiment(score: int) -> int:
        if score <= 2:
            return 0  # Negative / Complaint
        elif score == 3:
            return 1  # Neutral
        else:
            return 2  # Positive

    df["sentiment_label"] = df["review_score"].apply(map_sentiment)
    df["is_complaint"] = (df["review_score"] <= 2).astype(int)

    # Filter out empty text rows
    df_clean = df[df["cleaned_text"].str.len() > 3].reset_index(drop=True)
    logger.info(f"Extracted {len(df_clean):,} valid text reviews. Complaints: {df_clean['is_complaint'].sum():,} ({df_clean['is_complaint'].mean()*100:.1f}%)")
    return pd.DataFrame(df_clean)
