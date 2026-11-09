"""Authentication endpoints (login / refresh / me)."""
from fastapi import APIRouter, status

from app.api.deps import AuthSvc, CurrentUser
from app.core.exceptions import ValidationError
from app.schemas.auth import LoginRequest, RefreshRequest, TokenResponse
from app.schemas.user import UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(payload: LoginRequest, auth: AuthSvc) -> TokenResponse:
    return await auth.login(payload.email, payload.password)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(payload: RefreshRequest, auth: AuthSvc) -> TokenResponse:
    if not payload.refresh_token:
        raise ValidationError("refresh_token is required.")
    return await auth.refresh(payload.refresh_token)


@router.get("/me", response_model=UserResponse)
async def me(current_user: CurrentUser) -> UserResponse:
    return UserResponse.model_validate(current_user)