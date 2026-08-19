"""
Celery Asynchronous Task Queue Application and State Tracker.
"""

import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from celery import Celery

from src.api.config import settings

logger = logging.getLogger(__name__)

celery_app = Celery(
    "sales_intelligence_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
    broker_connection_timeout=0.5,
    broker_connection_retry_on_startup=False,
    broker_connection_max_retries=1,
)

# In-memory fallback task registry when running standalone without external Celery worker
TASK_REGISTRY: dict[str, dict[str, Any]] = {}


def register_task(task_type: str, initial_payload: dict[str, Any] | None = None) -> str:
    """Create and register a tracked task."""
    task_id = f"task_{uuid.uuid4().hex[:12]}"
    TASK_REGISTRY[task_id] = {
        "task_id": task_id,
        "task_type": task_type,
        "status": "PENDING",
        "result": None,
        "error": None,
        "payload": initial_payload or {},
        "created_at": datetime.now(UTC).isoformat(),
        "completed_at": None,
    }
    return task_id


def update_task(task_id: str, status: str, result: Any | None = None, error: str | None = None) -> None:
    """Update task state in the registry."""
    if task_id in TASK_REGISTRY:
        TASK_REGISTRY[task_id]["status"] = status
        TASK_REGISTRY[task_id]["result"] = result
        TASK_REGISTRY[task_id]["error"] = error
        if status in {"SUCCESS", "FAILURE", "REVOKED"}:
            TASK_REGISTRY[task_id]["completed_at"] = datetime.now(UTC).isoformat()


def get_task_status(task_id: str) -> dict[str, Any] | None:
    """Retrieve task state by ID."""
    return TASK_REGISTRY.get(task_id)
