"""Authentication endpoints: register, login, and current-user profile."""

from __future__ import annotations

from fastapi import APIRouter, status

from app.api.deps import CurrentUser, DbSession
from app.schemas.user import AuthResponse, UserCreate, UserLogin, UserRead
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


@router.get("/me", response_model=UserRead, summary="Get the current user's profile")
def me(current_user: CurrentUser) -> UserRead:
    return UserRead.model_validate(current_user)
