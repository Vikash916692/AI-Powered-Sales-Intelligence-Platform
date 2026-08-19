"""
Training pipeline for Product Recommendation Engine & Market Basket Analysis.
Computes item-to-item cosine similarity, category popularity indices, and association rules.
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
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity

from ml.recommendation.features import extract_order_baskets

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("ml.recommendation.train")

MODELS_DIR = Path(__file__).resolve().parent / "models"


def train_recommendation_engine() -> dict:
    """
    Build and serialize the item-to-item collaborative filtering and category affinity models.
    """
    logger.info("==================================================")
    logger.info("STARTING PRODUCT RECOMMENDATION ENGINE TRAINING")
    logger.info("==================================================")
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    df_baskets = extract_order_baskets()

    # 1. Product Popularity by Category (Cold-Start & Fallback Index)
    logger.info("Building Category-Level Popularity Index...")
    cat_pop = (
        df_baskets.groupby(["category_name_english", "product_id"])
        .size()
        .to_frame("order_count")
        .reset_index()
        .sort_values(["category_name_english", "order_count"], ascending=[True, False])
    )

    category_recommendations = {}
    for cat, group in cat_pop.groupby("category_name_english"):
        category_recommendations[str(cat)] = group.head(10)["product_id"].tolist()

    # 2. Item-to-Item Collaborative Filtering (Multi-Item Order Co-occurrences)
    logger.info("Building Item-to-Item Similarity Matrix on Multi-Item Orders...")
    order_counts = df_baskets["order_id"].value_counts().to_dict()
    multi_item_order_set = {oid for oid, cnt in order_counts.items() if cnt > 1}
    multi_df = df_baskets[df_baskets["order_id"].isin(multi_item_order_set)].copy()

    # Top popular products for sparse matrix
    top_pids_dict = set(df_baskets["product_id"].value_counts().head(5000).index)
    multi_filtered = multi_df[multi_df["product_id"].isin(top_pids_dict)].drop_duplicates()

    # Create mapping indices
    unique_orders = list(multi_filtered["order_id"].unique())
    unique_prods = list(multi_filtered["product_id"].unique())
    order_map = {oid: i for i, oid in enumerate(unique_orders)}
    prod_map = {pid: i for i, pid in enumerate(unique_prods)}
    inv_prod_map = {i: pid for pid, i in prod_map.items()}

    rows = [order_map[oid] for oid in multi_filtered["order_id"]]
    cols = [prod_map[pid] for pid in multi_filtered["product_id"]]
    vals = [1] * len(multi_filtered)

    # Sparse Order-Product Matrix: (Orders x Products) -> Transpose to (Products x Orders)
    sparse_matrix = csr_matrix((vals, (rows, cols)), shape=(len(order_map), len(prod_map)))
    item_matrix = sparse_matrix.T

    # Compute Item-Item Cosine Similarity
    item_sim = cosine_similarity(item_matrix, dense_output=False)

    # Build Top-N Similar Items lookup dictionary
    item_similarities = {}
    for pid, p_idx in prod_map.items():
        sim_row = item_sim[p_idx].toarray().flatten()
        sim_row[p_idx] = 0.0  # exclude self
        top_indices = sim_row.argsort()[::-1][:10]
        top_scores = [round(float(sim_row[idx]), 4) for idx in top_indices if sim_row[idx] > 0]
        top_pids = [inv_prod_map[idx] for idx in top_indices if sim_row[idx] > 0]
        if top_pids:
            item_similarities[pid] = list(zip(top_pids, top_scores, strict=False))

    logger.info(f"Item similarity model built: {len(item_similarities):,} products have direct co-occurrence recommendations.")

    # 3. Save Model Artifacts
    joblib.dump(item_similarities, MODELS_DIR / "item_similarities.joblib")
    joblib.dump(category_recommendations, MODELS_DIR / "category_recommendations.joblib")

    # Global Top 10 Best-Sellers
    global_top_10 = df_baskets["product_id"].value_counts().head(10).index.tolist()

    metadata_payload = {
        "model_name": "Product Recommendation & Cross-Sell Engine",
        "total_orders_evaluated": df_baskets["order_id"].nunique(),
        "total_products_indexed": len(df_baskets["product_id"].unique()),
        "categories_covered": len(category_recommendations),
        "products_with_collaborative_rules": len(item_similarities),
        "global_top_10": global_top_10,
        "created_at": datetime.now(UTC).isoformat(),
    }
    with open(MODELS_DIR / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata_payload, f, indent=4)

    metrics_payload = {
        "multi_item_orders_mined": len(multi_item_order_set),
        "products_indexed": len(prod_map),
        "similarity_coverage_rate": round(len(item_similarities) / max(len(prod_map), 1) * 100.0, 2),
    }
    with open(MODELS_DIR / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics_payload, f, indent=4)

    logger.info("Recommendation Engine training and serialization complete.")
    return metadata_payload


if __name__ == "__main__":
    train_recommendation_engine()
