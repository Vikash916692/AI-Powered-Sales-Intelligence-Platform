"""
Authentication package with password hashing, JWT, and user management.
"""

from src.api.auth.models import (
    DEMO_USERS_DB,
    UserInDB,
    create_user,
    get_user_by_username,
)
from src.api.auth.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)

__all__ = [
    "DEMO_USERS_DB",
    "UserInDB",
    "create_access_token",
    "create_user",
    "decode_access_token",
    "get_password_hash",
    "get_user_by_username",
    "verify_password",
]
