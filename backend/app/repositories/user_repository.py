"""
User-specific repository.

Notes:
    - `get_by_email` is the primary login lookup — email is unique + indexed.
    - `list_paginated` supports future admin user-management screens.
    - Soft-deleted users are excluded by default; `include_deleted=True` opt-in
      for compliance/audit queries.
"""
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    async def get_by_email(self, email: str, *, include_deleted: bool = False) -> User | None:
        stmt = select(User).where(User.email == email.lower())
        if not include_deleted:
            stmt = stmt.where(User.deleted_at.is_(None))
        stmt = stmt.options(selectinload(User.roles))
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def get_by_id(self, user_id: UUID, *, include_deleted: bool = False) -> User | None:
        stmt = select(User).where(User.id == user_id)
        if not include_deleted:
            stmt = stmt.where(User.deleted_at.is_(None))
        stmt = stmt.options(selectinload(User.roles))
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def list_paginated(
        self, *, page: int, page_size: int, include_deleted: bool = False
    ) -> tuple[list[User], int]:
        base = select(User)
        count_q = select(func.count()).select_from(User)
        if not include_deleted:
            base = base.where(User.deleted_at.is_(None))
            count_q = count_q.where(User.deleted_at.is_(None))
        total = int(await self.session.scalar(count_q) or 0)
        stmt = (
            base.options(selectinload(User.roles))
            .order_by(User.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        rows = (await self.session.execute(stmt)).scalars().all()
        return list(rows), total