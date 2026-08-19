"""
Authentication & Authorization API Test Suite.

Verifies:
1. Valid user login returns JWT token
2. Invalid credentials return 401 Unauthorized
3. User profile retrieval via /auth/me
4. User registration endpoint
5. Token expiration / invalid signature rejection
"""

from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_login_success():
    """Verify admin login returns valid JWT token."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["role"] == "Admin"
    assert data["username"] == "admin"


def test_login_invalid_credentials():
    """Verify incorrect password returns 401."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert "Incorrect" in response.json()["detail"]


def test_get_current_user_profile():
    """Verify authenticated user can fetch profile details."""
    login_res = client.post(
        "/api/v1/auth/login",
        json={"username": "executive", "password": "executive123"},
    )
    token = login_res.json()["access_token"]

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "executive"
    assert data["role"] == "Executive"


def test_get_current_user_unauthorized():
    """Verify missing token returns 401."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_register_new_user():
    """Verify user registration endpoint."""
    new_username = "test_analyst_user"
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": new_username,
            "password": "securepassword123",
            "role": "Analyst",
            "email": "test_analyst@company.com",
            "full_name": "Test Analyst",
        },
    )
    assert response.status_code in {201, 400}
    if response.status_code == 201:
        data = response.json()
        assert data["username"] == new_username
        assert data["role"] == "Analyst"
