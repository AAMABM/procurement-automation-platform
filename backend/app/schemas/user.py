"""User schemas — used by admin CRUD and /me endpoints."""
from datetime import datetime
from uuid import UUID

from pydantic import EmailStr, Field

from app.schemas.common import ORMModel


class RoleSummary(ORMModel):
    id: UUID
    name: str


class UserResponse(ORMModel):
    id: UUID
    email: EmailStr
    full_name: str
    is_active: bool
    is_superuser: bool
    last_login_at: datetime | None
    created_at: datetime
    updated_at: datetime
    roles: list[RoleSummary]


class UserCreate(ORMModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=1, max_length=255)
    is_active: bool = True
    role_ids: list[UUID] = Field(default_factory=list)


class UserUpdate(ORMModel):
    full_name: str | None = Field(None, min_length=1, max_length=255)
    password: str | None = Field(None, min_length=8, max_length=128)
    is_active: bool | None = None
    role_ids: list[UUID] | None = None