"""
Asynchronous Background Task Management Endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.cache import cache
from src.api.dependencies import get_current_user, require_role
from src.api.schemas.auth_schemas import UserRead
from src.api.schemas.task_schemas import AsyncRCARequest, TaskStatusResponse
from src.api.workers.celery_app import get_task_status, register_task
from src.api.workers.tasks import async_run_rca

router = APIRouter(prefix="/tasks", tags=["Asynchronous Task Queue (Celery)"])


@router.post(
    "/rca-async",
    response_model=TaskStatusResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Dispatch asynchronous Root Cause Analysis diagnostic job",
)
def trigger_async_rca(
    request: AsyncRCARequest,
    current_user: UserRead = Depends(require_role(["Admin", "Executive", "Analyst"])),
):
    """
    Dispatches a heavy Root Cause Analysis job to background Celery workers
    and returns a trackable task ID.
    """
    task_id = register_task("rca_diagnostic", {"inquiry": request.inquiry})

    # If Redis is active, dispatch to Celery worker; otherwise run inline fallback
    if cache.is_redis:
        try:
            async_run_rca.delay(inquiry=request.inquiry, task_id=task_id)
        except Exception:
            async_run_rca(inquiry=request.inquiry, task_id=task_id)
    else:
        async_run_rca(inquiry=request.inquiry, task_id=task_id)

    task_state = get_task_status(task_id)
    return TaskStatusResponse(**task_state)


@router.get(
    "/{task_id}",
    response_model=TaskStatusResponse,
    summary="Get status and output of an asynchronous task",
)
def get_task(
    task_id: str,
    current_user: UserRead = Depends(get_current_user),
):
    """Inspect status (PENDING, STARTED, SUCCESS, FAILURE) and output payload of a task."""
    state = get_task_status(task_id)
    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID '{task_id}' not found.",
        )
    return TaskStatusResponse(**state)
