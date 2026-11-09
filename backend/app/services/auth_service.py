"""
Authentication service.

Responsibilities:
    - Verify credentials.
    - Issue access + refresh tokens.
    - Record `last_login_at` (audit + inactivity reporting).
    - Reject disabled/deleted users.

Why a service and not in the route?
    Routes should only translate HTTP ↔ domain. Keeping business logic here
    makes it callable from CLI tools, background jobs, and tests without HTTP
    overhead — critical for future SSO/JIT provisioning.

Security notes:
    - Timing: we verify a dummy hash even when the user doesn't exist, to
      prevent user-enumeration via response-time analysis.
    - Generic error messages: never reveal whether the email exists.
"""
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenResponse

# Pre-computed hash used for constant-time failure on unknown users.
_DUMMY_HASH = hash_password("dummy_password_for_timing_only")


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.users = UserRepository(session)
        self.settings = get_settings()

    async def authenticate(self, email: str, password: str) -> User:
        user = await self.users.get_by_email(email)
        # Constant-time defense against user enumeration
        if user is None:
            verify_password(password, _DUMMY_HASH)
            raise AuthenticationError("Invalid email or password.")
        if not verify_password(password, user.hashed_password):
            raise AuthenticationError("Invalid email or password.")
        if not user.is_active:
            raise AuthorizationError("This account is disabled.", code="account_disabled")
        return user

    async def login(self, email: str, password: str) -> TokenResponse:
        user = await self.authenticate(email, password)
        user.last_login_at = datetime.now(UTC)
        await self.session.commit()

        access = create_access_token(str(user.id))
        refresh = create_refresh_token(str(user.id))
        return TokenResponse(
            access_token=access,
            refresh_token=refresh,
            expires_in=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def refresh(self, refresh_token: str) -> TokenResponse:
        payload = decode_token(refresh_token, expected_type="refresh")
        user_id = payload["sub"]
        user = await self.users.get_by_id(user_id)
        if user is None or not user.is_active:
            raise AuthenticationError("Account no longer active.", code="account_disabled")
        access = create_access_token(str(user.id))
        # Phase 2 will rotate refresh tokens (server-side family + reuse detection)
        new_refresh = create_refresh_token(str(user.id))
        return TokenResponse(
            access_token=access,
            refresh_token=new_refresh,
            expires_in=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )