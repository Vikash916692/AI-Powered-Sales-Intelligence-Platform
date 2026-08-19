"""
Async Task Execution and Status Schemas for Celery.
"""

from typing import Any

from pydantic import BaseModel, Field


class AsyncRCARequest(BaseModel):
    """Request to trigger asynchronous deep-dive Root Cause Analysis."""

    inquiry: str = Field(
        default="Why are customer delivery delays spiking in Southeast routes?",
        description="Business anomaly to diagnose",
    )


class TaskStatusResponse(BaseModel):
    """Status and result of an asynchronous task."""

    task_id: str
    status: str = Field(..., description="PENDING, STARTED, SUCCESS, FAILURE, REVOKED")
    result: Any | None = None
    error: str | None = None
    created_at: str | None = None
