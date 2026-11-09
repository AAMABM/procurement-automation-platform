"""
Async database engine + session factory.

Why this exists:
    Single place to configure the connection pool, echo, and session lifecycle.
    Async is chosen for FastAPI because: (a) procurement endpoints are I/O-bound
    (DB + external ERP calls), (b) async scales concurrency per worker without
    spawning threads, (c) aligns with future OData calls to S/4HANA.

Enterprise decisions:
    - `pool_pre_ping=True` — recovers from dropped connections after idle
      (critical behind load balancers and cloud RDS).
    - `pool_size` + `max_overflow` tuned for typical web workloads.
    - Session is created per-request via FastAPI dependency, never shared.
    - `expire_on_commit=False` prevents detached-object errors when returning
      ORM objects across the service → API boundary.

Tradeoff:
    Async SQLAlchemy adds cognitive overhead. For a procurement system with
    heavy ERP integrations (latency-bound), the concurrency win is well worth it.
"""
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings

_settings = get_settings()

engine = create_async_engine(
    _settings.DATABASE_URL,
    echo=_settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_recycle=1800,          # recycle every 30 min — safe behind RDS/ALB
    future=True,
)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields a request-scoped session.
    Commits are explicit in the service layer (unit-of-work pattern).

    Rationale: automatic commit on teardown hides transaction boundaries.
    In a procurement system touching money, every commit should be deliberate.
    """
    async with SessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()