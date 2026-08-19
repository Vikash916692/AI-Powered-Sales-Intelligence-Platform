"""
Authentication Endpoints: Login, Registration, Token Refresh, and User Profile.
"""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.api.auth.models import create_user, get_user_by_username
from src.api.auth.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)
from src.api.config import settings
from src.api.dependencies import get_current_user
from src.api.schemas.auth_schemas import LoginRequest, Token, UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["Authentication & Access Control"])


@router.post("/login", response_model=Token, summary="Authenticate and obtain JWT bearer token")
async def login_json(credentials: LoginRequest):
    """
    Authenticate with username and password.
    Returns signed JWT access token and user role.
    """
    user = get_user_by_username(credentials.username)
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires,
    )

    return Token(
        access_token=token,
        token_type="bearer",
        expires_in_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        role=user.role,
        username=user.username,
    )


@router.post("/token", response_model=Token, summary="OAuth2 form-compatible login endpoint")
async def login_oauth2(form_data: OAuth2PasswordRequestForm = Depends()):
    """OAuth2 password form login compatible with Swagger UI authorization modal."""
    return await login_json(LoginRequest(username=form_data.username, password=form_data.password))


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED, summary="Register a new user")
async def register(user_in: UserCreate):
    """Register a new user profile."""
    existing = get_user_by_username(user_in.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    pwd_hash = get_password_hash(user_in.password)
    new_user = create_user(
        username=user_in.username,
        password_hash=pwd_hash,
        role=user_in.role,
        email=user_in.email,
        full_name=user_in.full_name,
    )
    return UserRead(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        full_name=new_user.full_name,
        role=new_user.role,
        is_active=new_user.is_active,
    )


@router.get("/me", response_model=UserRead, summary="Get current authenticated user profile")
async def read_current_user(current_user: UserRead = Depends(get_current_user)):
    """Retrieve profile and roles for the currently authenticated user."""
    return current_user
