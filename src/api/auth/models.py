"""
User Model & Repository with seeded demo accounts for RBAC.
"""


from src.api.auth.security import get_password_hash
from src.api.schemas.auth_schemas import UserRead


class UserInDB(UserRead):
    """User representation stored with hashed credentials."""

    hashed_password: str


# Seeded production and testing users across all RBAC roles
DEMO_USERS_DB: dict[str, UserInDB] = {
    "admin": UserInDB(
        id="usr_admin_01",
        username="admin",
        email="admin@sales-intelligence.ai",
        full_name="Platform Administrator",
        role="Admin",
        is_active=True,
        hashed_password=get_password_hash("admin123"),
    ),
    "executive": UserInDB(
        id="usr_exec_02",
        username="executive",
        email="csuite@sales-intelligence.ai",
        full_name="Chief Executive Officer",
        role="Executive",
        is_active=True,
        hashed_password=get_password_hash("executive123"),
    ),
    "analyst": UserInDB(
        id="usr_analyst_03",
        username="analyst",
        email="analyst@sales-intelligence.ai",
        full_name="Senior Sales Analyst",
        role="Analyst",
        is_active=True,
        hashed_password=get_password_hash("analyst123"),
    ),
    "viewer": UserInDB(
        id="usr_viewer_04",
        username="viewer",
        email="viewer@sales-intelligence.ai",
        full_name="Guest Viewer",
        role="Viewer",
        is_active=True,
        hashed_password=get_password_hash("viewer123"),
    ),
}


def get_user_by_username(username: str) -> UserInDB | None:
    """Look up user record by username."""
    return DEMO_USERS_DB.get(username.lower())


def create_user(username: str, password_hash: str, role: str = "Viewer", email: str | None = None, full_name: str | None = None) -> UserInDB:
    """Register and persist a new user in the repository."""
    user = UserInDB(
        id=f"usr_{len(DEMO_USERS_DB) + 1:02d}",
        username=username.lower(),
        email=email,
        full_name=full_name or username.title(),
        role=role,
        is_active=True,
        hashed_password=password_hash,
    )
    DEMO_USERS_DB[username.lower()] = user
    return user
