"""
Aggregated v1 Master API Router.
"""

from fastapi import APIRouter

from src.api.v1.endpoints import (
    agents,
    analytics,
    auth,
    health,
    kpis,
    ml,
    reports,
    tasks,
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(kpis.router)
api_router.include_router(analytics.router)
api_router.include_router(ml.router)
api_router.include_router(agents.router)
api_router.include_router(reports.router)
api_router.include_router(tasks.router)
api_router.include_router(health.router)
