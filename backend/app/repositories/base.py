"""
Generic repository.

Why this exists:
    Encapsulates all SQLAlchemy interactions. Services depend on repository
    interfaces, never on ORM directly — enabling in-memory fakes in unit tests
    and a future swap (e.g., read replicas) without touching business logic.

SOLID:
    S — one responsibility: persistence.
    O — extensible via subclass overrides.
    L — every subclass can be used where a BaseRepository is expected.
    I — narrow surface area.
    D — services depend on the abstraction.

Tradeoff:
    Generic repos save boilerplate but can leak ORM semantics (e.g., eager
    loading). Subclasses override for complex queries rather than fight the
    generic base — see UserRepository.list_paginated.
"""
from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, id_: UUID) -> ModelT | None:
        return await self.session.get(self.model, id_)

    async def get_by(self, **filters) -> ModelT | None:
        stmt = select(self.model).filter_by(**filters).limit(1)
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def add(self, obj: ModelT) -> ModelT:
        self.session.add(obj)
        await self.session.flush()          # assign PK without commit
        return obj

    async def delete(self, obj: ModelT) -> None:
        await self.session.delete(obj)
        await self.session.flush()

    async def count(self) -> int:
        return int(await self.session.scalar(select(func.count()).select_from(self.model)) or 0)