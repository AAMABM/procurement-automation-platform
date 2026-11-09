"""
User management service.

Covers admin CRUD + `/me` lookups. Business rules enforced here (not in DB
constraints) for clarity and consistent error messages:

    - email uniqueness case-insensitively
    - can't deactivate / delete yourself
    - system roles are immutable
    - password changes use the same hashing path as creation
"""
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    AuthorizationError,
    ConflictError,
    NotFoundError,
    ValidationError,
)
from app.core.security import hash_password
from app.models.user import User
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.users = UserRepository(session)
        self.roles = RoleRepository(session)

    async def get(self, user_id: UUID) -> User:
        user = await self.users.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found.")
        return user

    async def get_by_email(self, email: str) -> User | None:
        return await self.users.get_by_email(email)

    async def list(self, *, page: int, page_size: int) -> tuple[list[User], int]:
        return await self.users.list_paginated(page=page, page_size=page_size)

    async def create(self, payload: UserCreate) -> User:
        existing = await self.users.get_by_email(payload.email, include_deleted=True)
        if existing:
            raise ConflictError("A user with this email already exists.")

        roles = await self.roles.get_many(payload.role_ids)
        if len(roles) != len(set(payload.role_ids)):
            raise ValidationError("One or more role IDs are invalid.")

        user = User(
            email=payload.email.lower(),
            hashed_password=hash_password(payload.password),
            full_name=payload.full_name,
            is_active=payload.is_active,
            roles=roles,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update(self, user_id: UUID, payload: UserUpdate, *, acting_user: User) -> User:
        user = await self.get(user_id)

        if payload.is_active is False and user.id == acting_user.id:
            raise ValidationError("You cannot deactivate your own account.")

        if payload.full_name is not None:
            user.full_name = payload.full_name
        if payload.password is not None:
            user.hashed_password = hash_password(payload.password)
        if payload.is_active is not None:
            user.is_active = payload.is_active
        if payload.role_ids is not None:
            roles = await self.roles.get_many(payload.role_ids)
            if len(roles) != len(set(payload.role_ids)):
                raise ValidationError("One or more role IDs are invalid.")
            user.roles = roles

        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete(self, user_id: UUID, *, acting_user: User) -> None:
        if user_id == acting_user.id:
            raise ValidationError("You cannot delete your own account.")
        user = await self.get(user_id)
        user.is_active = False            # soft-disable before soft-delete
        user.deleted_at = user.updated_at
        await self.session.commit()