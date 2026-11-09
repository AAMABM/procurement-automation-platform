"""Test fixtures.

Why:
    - `aiosqlite` in-memory DB = fast, isolated tests, no Docker required.
    - `StaticPool` is MANDATORY for SQLite `:memory:` because each connection
      normally gets its OWN database; StaticPool shares one connection so
      seeded data is visible across fixtures.
    - `client` depends on `session` so the DB is seeded before the app starts.
"""
import asyncio
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.init_db import init_db
from app.db.session import get_db
from app.main import create_app



@pytest_asyncio.fixture
async def engine():
    eng = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,          # <-- single shared connection
    )
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    await eng.dispose()


@pytest_asyncio.fixture
async def session(engine) -> AsyncIterator[AsyncSession]:
    maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with maker() as s:
        await init_db(s)
        yield s


@pytest_asyncio.fixture
async def client(engine, session) -> AsyncIterator[AsyncClient]:
    """`session` is a *dependency* here: it guarantees seeding runs first."""
    maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async def override_get_db():
        async with maker() as s:
            yield s

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    app.router.lifespan_context = _noop_lifespan

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c


@asynccontextmanager
async def _noop_lifespan(_app):
    yield