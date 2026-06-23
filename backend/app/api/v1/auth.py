"""Authentication endpoints: register, login, and current-user profile."""

from __future__ import annotations

from fastapi import APIRouter, status

from app.api.deps import CurrentUser, DbSession
from app.schemas.base import MessageResponse
from app.schemas.user import (
    AuthResponse,
    PasswordChange,
    ProfileUpdate,
    RefreshRequest,
    UserCreate,
    UserLogin,
    UserRead,
)
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new account",
)
def register(data: UserCreate, db: DbSession) -> AuthResponse:
    return AuthService(db).register(data)


@router.post("/login", response_model=AuthResponse, summary="Authenticate and receive a token")
def login(data: UserLogin, db: DbSession) -> AuthResponse:
    return AuthService(db).authenticate(data.email, data.password)


@router.post("/refresh", response_model=AuthResponse, summary="Rotate tokens via refresh token")
def refresh(data: RefreshRequest, db: DbSession) -> AuthResponse:
    return AuthService(db).refresh(data.refresh_token)


@router.get("/me", response_model=UserRead, summary="Get the current user's profile")
def me(current_user: CurrentUser) -> UserRead:
    return UserRead.model_validate(current_user)


@router.patch("/me", response_model=UserRead, summary="Update the current user's profile")
def update_me(data: ProfileUpdate, current_user: CurrentUser, db: DbSession) -> UserRead:
    user = AuthService(db).update_profile(current_user, data.full_name)
    return UserRead.model_validate(user)


@router.post(
    "/change-password",
    response_model=MessageResponse,
    summary="Change the current user's password",
)
def change_password(
    data: PasswordChange, current_user: CurrentUser, db: DbSession
) -> MessageResponse:
    AuthService(db).change_password(current_user, data.current_password, data.new_password)
    return MessageResponse(message="Password updated successfully.")
