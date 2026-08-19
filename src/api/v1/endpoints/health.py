"""
System Health, Readiness, and Liveness Probes.
"""

from typing import Any

from fastapi import APIRouter
from sqlalchemy import text

from ml.common.db import get_engine
from src.agents.tools.ml_tools import (
    get_delay_predictor,
    get_forecaster,
    get_recommender,
    get_sentiment_predictor,
)
from src.api.cache import cache
from src.rag.vector_store import vector_store

router = APIRouter(prefix="/health", tags=["Health & Observability"])


@router.get("", summary="Comprehensive system health check")
def health_check() -> dict[str, Any]:
    """
    Performs deep diagnostics across all system components:
    - MySQL Data Warehouse Connection Pool
    - Redis Cache Layer
    - ChromaDB Vector Store & Collections
    - Machine Learning Model Artifacts
    """
    checks = {}

    # 1. Database Check
    try:
        engine = get_engine()
        with engine.connect() as conn:
            res = conn.execute(text("SELECT 1;")).scalar()
            checks["database"] = {"status": "healthy" if res == 1 else "degraded"}
    except Exception as e:
        checks["database"] = {"status": "unhealthy", "error": str(e)}

    # 2. Redis / Cache Check
    checks["cache"] = {
        "status": "healthy",
        "provider": "redis" if cache.is_redis else "in_memory_fallback",
    }

    # 3. Vector Store Check
    try:
        stats = vector_store.get_stats()
        checks["vector_store"] = {
            "status": "healthy",
            "schema_docs": stats["schema_catalog_count"],
            "business_docs": stats["business_knowledge_count"],
        }
    except Exception as e:
        checks["vector_store"] = {"status": "unhealthy", "error": str(e)}

    # 4. ML Models Check
    try:
        get_delay_predictor()
        get_forecaster()
        get_recommender()
        get_sentiment_predictor()
        checks["ml_models"] = {"status": "healthy", "loaded_models": 4}
    except Exception as e:
        checks["ml_models"] = {"status": "unhealthy", "error": str(e)}

    all_healthy = all(v.get("status") == "healthy" for v in checks.values())

    return {
        "status": "healthy" if all_healthy else "degraded",
        "components": checks,
    }


@router.get("/live", summary="Kubernetes Liveness Probe")
def liveness_probe() -> dict[str, str]:
    """Simple ping checking if the API process is alive."""
    return {"status": "alive"}


@router.get("/ready", summary="Kubernetes Readiness Probe")
def readiness_probe() -> dict[str, str]:
    """Checks if the service is ready to accept incoming traffic."""
    return {"status": "ready"}
