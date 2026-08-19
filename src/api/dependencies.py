"""
FastAPI Dependency Injection Providers for Authentication, RBAC, and Caching.
"""

from collections.abc import Callable

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.api.auth.models import UserInDB, get_user_by_username
from src.api.auth.security import decode_access_token
from src.api.cache import CacheManager, cache
from src.api.schemas.auth_schemas import UserRead

security_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    auth: HTTPAuthorizationCredentials | None = Security(security_bearer),
) -> UserRead:
    """
    Extracts and verifies JWT bearer token from Authorization header.
    """
    if not auth or not auth.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(auth.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid, expired, or corrupted token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username: str | None = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials payload.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user: UserInDB | None = get_user_by_username(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found in system.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account.",
        )

    return UserRead(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
    )


def require_role(allowed_roles: list[str]) -> Callable:
    """
    Factory creating a dependency that enforces Role-Based Access Control (RBAC).

    Allowed roles hierarchy:
    - Admin: Superuser with access to all endpoints
    - Executive: C-suite overview, reports, ML, RCA, Agents
    - Analyst: Deep data marts, SQL, ML, KPIs
    - Viewer: Read-only KPIs & basic analytics
    """

    async def role_checker(
        current_user: UserRead = Depends(get_current_user),
    ) -> UserRead:
        if "Admin" in current_user.role:
            return current_user

        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden: User role '{current_user.role}' lacks required permissions ({allowed_roles}).",
            )
        return current_user

    return role_checker


def get_cache() -> CacheManager:
    """Provides cache singleton."""
    return cache
