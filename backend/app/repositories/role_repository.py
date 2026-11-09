"""Role repository — used by role assignment and RBAC checks."""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.role import Role
from app.repositories.base import BaseRepository


class RoleRepository(BaseRepository[Role]):
    model = Role

    async def get_many(self, role_ids: list[UUID]) -> list[Role]:
        if not role_ids:
            return []
        stmt = (
            select(Role)
            .where(Role.id.in_(role_ids))
            .options(selectinload(Role.permissions))
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def list_all(self) -> list[Role]:
        stmt = select(Role).options(selectinload(Role.permissions)).order_by(Role.name)
        return list((await self.session.execute(stmt)).scalars().all())

    async def get_by_name(self, name: str) -> Role | None:
        stmt = (
            select(Role).where(Role.name == name).options(selectinload(Role.permissions))
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()