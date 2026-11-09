"""
Cryptographic primitives: password hashing + JWT issuing/verification.

Why this exists:
    All security-sensitive code lives in one module so it can be reviewed,
    tested, and rotated independently of business logic.

Enterprise decisions:
    - Argon2id via pwdlib for passwords (OWASP recommended).
    - Access + refresh token split: short-lived access (15 min) limits
      exposure; refresh (7 days) supports SSO-like UX.
    - JWT payload carries `sub` (user id), `type` (access|refresh), `jti`,
      `iat`, `exp`, `iss`, `aud` — required for downstream verification.
    - Refresh tokens will be DB-tracked in Phase 2 for revocation; for
      Phase 1, they're stateless JWTs (documented tradeoff).

SAP S/4HANA relevance:
    Access tokens authenticate API-first flows (Fiori → S/4HANA OData).
    In BTP deployments this module would be swapped for XSUAA tokens;
    keeping it isolated makes that swap trivial.
"""
from datetime import UTC, datetime, timedelta
from typing import Any, Literal
from uuid import uuid4

import jwt
from pwdlib import PasswordHash

from app.core.config import get_settings
from app.core.exceptions import AuthenticationError

_password_hasher = PasswordHash.recommended()
TokenType = Literal["access", "refresh"]


# ---------- Passwords ----------

def hash_password(plain: str) -> str:
    return _password_hasher.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return _password_hasher.verify(plain, hashed)
    except Exception:  # noqa: BLE001 — hash corruption must not crash login
        return False


# ---------- JWT ----------

def _create_token(subject: str, token_type: TokenType, expires_delta: timedelta) -> str:
    settings = get_settings()
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "jti": str(uuid4()),
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
        "iss": "procurement-platform",
        "aud": "procurement-platform-api",
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(subject: str) -> str:
    settings = get_settings()
    return _create_token(
        subject, "access", timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )


def create_refresh_token(subject: str) -> str:
    settings = get_settings()
    return _create_token(
        subject, "refresh", timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )


def decode_token(token: str, *, expected_type: TokenType) -> dict[str, Any]:
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            audience="procurement-platform-api",
            issuer="procurement-platform",
        )
    except jwt.ExpiredSignatureError as exc:
        raise AuthenticationError("Token has expired.", code="token_expired") from exc
    except jwt.InvalidTokenError as exc:
        raise AuthenticationError("Invalid token.", code="token_invalid") from exc

    if payload.get("type") != expected_type:
        raise AuthenticationError(
            f"Expected a {expected_type} token.", code="token_type_mismatch"
        )
    return payload