"""
Asynchronous Celery Task Endpoints Test Suite.

Verifies:
1. /tasks/rca-async dispatches background task
2. /tasks/{task_id} tracks status and retrieves output
3. 404 for unknown task IDs
"""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


@pytest.fixture
def auth_header():
    res = client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_async_rca_task_dispatch_and_polling(auth_header):
    """Verify dispatching background task and inspecting status."""
    # 1. Trigger task
    response = client.post(
        "/api/v1/tasks/rca-async",
        headers=auth_header,
        json={"inquiry": "Why did sales drop in August?"},
    )
    assert response.status_code == 202
    data = response.json()
    task_id = data["task_id"]
    assert task_id.startswith("task_")

    # 2. Poll task status
    status_res = client.get(f"/api/v1/tasks/{task_id}", headers=auth_header)
    assert status_res.status_code == 200
    state_data = status_res.json()
    assert state_data["task_id"] == task_id
    assert state_data["status"] in {"PENDING", "STARTED", "SUCCESS"}


def test_get_nonexistent_task(auth_header):
    """Verify 404 for invalid task ID."""
    response = client.get("/api/v1/tasks/nonexistent_task_9999", headers=auth_header)
    assert response.status_code == 404
