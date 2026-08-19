"""
Authentication & User Pydantic Schemas.
"""


from pydantic import BaseModel, Field


class Token(BaseModel):
    """JWT Token response schema."""

    access_token: str
    token_type: str = "bearer"
    expires_in_seconds: int
    role: str
    username: str


class TokenPayload(BaseModel):
    """Decoded JWT Token payload."""

    sub: str | None = None
    role: str | None = "Viewer"
    exp: int | None = None


class LoginRequest(BaseModel):
    """User login request credentials."""

    username: str = Field(..., description="Username or email address")
    password: str = Field(..., description="User password")


class UserBase(BaseModel):
    """Base user profile schema."""

    username: str
    email: str | None = None
    full_name: str | None = None
    role: str = Field(default="Viewer", description="User role: Admin, Executive, Analyst, Viewer")
    is_active: bool = True


class UserRead(UserBase):
    """User profile response schema."""

    id: str


class UserCreate(UserBase):
    """User registration schema."""

    password: str = Field(..., min_length=6)
