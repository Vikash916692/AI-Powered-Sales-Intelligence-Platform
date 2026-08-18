"""
Inference pipeline for Product Recommendation Engine & Cross-Sell.
Provides item-to-item recommendations, category-based recommendations, and popular best-sellers.
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

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("ml.recommendation.predict")

MODELS_DIR = Path(__file__).resolve().parent / "models"


class RecommendationEngine:
    """
    Production Recommendation Engine for Cross-Sell & Upsell.
    """

    def __init__(self, model_dir: str | Path | None = None):
        self.model_dir = Path(model_dir) if model_dir else MODELS_DIR
        self.item_sim_path = self.model_dir / "item_similarities.joblib"
        self.cat_rec_path = self.model_dir / "category_recommendations.joblib"
        self.metadata_path = self.model_dir / "metadata.json"

        if not self.item_sim_path.exists() or not self.cat_rec_path.exists():
            raise FileNotFoundError(
                f"Recommendation artifacts not found at {self.model_dir}. Please run train.py first."
            )

        self.item_similarities = joblib.load(self.item_sim_path)
        self.category_recommendations = joblib.load(self.cat_rec_path)

        with open(self.metadata_path, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)

        self.global_top_10 = self.metadata.get("global_top_10", [])

    def recommend_for_product(self, product_id: str, top_n: int = 5) -> list[dict]:
        """
        Get collaborative cross-sell recommendations for a specific product.
        Falls back to global best-sellers if fewer than top_n collaborative pairs exist.
        """
        recs = []
        seen_pids = {product_id}
        if product_id in self.item_similarities:
            for pid, score in self.item_similarities[product_id]:
                if pid not in seen_pids:
                    seen_pids.add(pid)
                    recs.append({"product_id": pid, "similarity_score": score, "method": "collaborative_filtering"})
                if len(recs) >= top_n:
                    return recs

        # Pad with global top best-sellers if needed
        for pid in self.global_top_10:
            if pid not in seen_pids:
                seen_pids.add(pid)
                recs.append({"product_id": pid, "similarity_score": 1.0, "method": "category_popularity_fallback"})
            if len(recs) >= top_n:
                break

        return recs

    def recommend_for_category(self, category_name: str, top_n: int = 5) -> list[str]:
        """
        Get best-selling products within a specific category.
        """
        return self.category_recommendations.get(category_name, self.global_top_10)[:top_n]

    def recommend_for_basket(self, product_ids: list[str], top_n: int = 5) -> pd.DataFrame:
        """
        Generate ranked recommendations for a multi-item cart.
        """
        candidate_scores = {}
        for pid in product_ids:
            if pid in self.item_similarities:
                for target_pid, score in self.item_similarities[pid]:
                    if target_pid not in product_ids:
                        candidate_scores[target_pid] = candidate_scores.get(target_pid, 0.0) + score

        if not candidate_scores:
            for pid in self.global_top_10:
                if pid not in product_ids:
                    candidate_scores[pid] = 0.5

        sorted_candidates = sorted(candidate_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
        return pd.DataFrame([{"recommended_product_id": pid, "confidence_score": round(score, 4)} for pid, score in sorted_candidates])


def recommend_sample_demo():
    engine = RecommendationEngine()
    test_pid = engine.global_top_10[0] if engine.global_top_10 else "test_product"
    recs = engine.recommend_for_product(test_pid, top_n=5)
    print("\n" + "=" * 65)
    print(f"PRODUCT RECOMMENDATIONS FOR ITEM: {test_pid}")
    print("=" * 65)
    df = pd.DataFrame(recs)
    print(df.to_string(index=False))
    print("=" * 65)
    return df


if __name__ == "__main__":
    recommend_sample_demo()
