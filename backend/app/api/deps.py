"""
FastAPI dependency providers — the composition root for the HTTP layer.

Why this exists:
    Centralizes object construction (services, repositories, current user).
    Routes declare *what they need*, not *how to build it*.

Enterprise decisions:
    - `get_current_user` performs the full auth path in one dependency,
      composable via `Depends`.
    - `require_permissions(...)` is a factory — future routes use
      `Depends(require_permissions(PermissionCode.PURCHASE_ORDERS_APPROVE))`.
    - All 401s use the RFC 6750 `WWW-Authenticate: Bearer` header.

SAP S/4HANA relevance:
    Analogous to SAP's authorization check (`AUTHORITY-CHECK OBJECT ...`).
    Here it's declarative at the route boundary, enabling easy review by
    security auditors.
"""
from collections.abc import Callable
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.user_service import UserService

_settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{_settings.API_V1_PREFIX}/auth/login", auto_error=False
)


async def get_db_session() -> AsyncSession:  # explicit alias for readability
    async for s in get_db():
        yield s


DB = Annotated[AsyncSession, Depends(get_db_session)]


def get_auth_service(session: DB) -> AuthService:
    return AuthService(session)


def get_user_service(session: DB) -> UserService:
    return UserService(session)


AuthSvc = Annotated[AuthService, Depends(get_auth_service)]
UserSvc = Annotated[UserService, Depends(get_user_service)]


async def get_current_user(
    token: Annotated[str | None, Depends(oauth2_scheme)],
    session: DB,
) -> User:
    if not token:
        raise AuthenticationError("Authentication required.", code="missing_token")
    payload = decode_token(token, expected_type="access")
    try:
        user_id = UUID(payload["sub"])
    except (KeyError, ValueError) as exc:
        raise AuthenticationError("Malformed token.", code="token_malformed") from exc

    user = await UserRepository(session).get_by_id(user_id)
    if user is None or not user.is_active:
        raise AuthenticationError("Account is inactive.", code="account_disabled")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_permissions(*required: str) -> Callable[..., User]:
    """
    Factory returning a dependency that enforces ALL given permission codes.

    Usage:
        @router.post("/orders/{id}/approve",
                     dependencies=[Depends(require_permissions("purchase_orders:approve"))])
    """
    async def _checker(user: CurrentUser) -> User:
        granted = user.permission_codes
        if "*" in granted:  # superuser
            return user
        missing = [p for p in required if p not in granted]
        if missing:
            raise AuthorizationError(
                "Missing required permissions.",
                code="insufficient_permissions",
                details={"missing": missing},
            )
        return user

    return _checker


def get_request_id(x_request_id: Annotated[str | None, Header(alias="X-Request-ID")] = None) -> str | None:
    return x_request_id

# Add these imports at the top with the others:
from app.services.vendor_service import VendorService
from app.services.requisition_service import PRService

# Add these to the bottom of the file:
def get_vendor_service(session: DB) -> VendorService:
    return VendorService(session)

def get_pr_service(session: DB) -> PRService:
    return PRService(session)

VendorSvc = Annotated[VendorService, Depends(get_vendor_service)]
PRSvc = Annotated[PRService, Depends(get_pr_service)]

from app.services.purchase_order_service import POService

def get_po_service(session: DB) -> POService:
    return POService(session)

POSvc = Annotated[POService, Depends(get_po_service)]