"""
Application factory — wires together every layer.

Why a factory (`create_app`)?
    - Tests instantiate a fresh app with overridden config.
    - Multiple entrypoints (API, CLI, worker) can share the app config.
    - Avoids module-level side effects, enabling safe imports.

Middleware order (outermost → innermost):
    1. CORS         — must see preflight responses even on auth failures.
    2. RequestContext — binds request_id for all downstream logs.
    3. AccessLog    — needs request_id to correlate.

Lifecycle:
    - Startup: seed system roles/permissions (idempotent).
    - Shutdown: dispose DB pool cleanly (avoids "connection refused" warnings
      during rolling restarts).
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging, get_logger
from app.db.init_db import init_db
from app.db.session import SessionLocal, engine
from app.middleware.request_context import RequestContextMiddleware
from app.middleware.request_logging import AccessLogMiddleware

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    logger.info("app_startup", env=settings.APP_ENV, version=__version__)
    async with SessionLocal() as session:
        try:
            await init_db(session)
        except Exception as exc:  # noqa: BLE001
            logger.exception("db_init_failed", error=str(exc))
            raise
    yield
    await engine.dispose()
    logger.info("app_shutdown")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.APP_NAME,
        version=__version__,
        openapi_url="/openapi.json",
        docs_url="/docs" if settings.APP_ENV != "production" else None,
        redoc_url="/redoc" if settings.APP_ENV != "production" else None,
        lifespan=lifespan,
    )

    # --- Middleware (order matters) ---
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )
    app.add_middleware(AccessLogMiddleware)
    app.add_middleware(RequestContextMiddleware)

    # --- Error handlers ---
    register_exception_handlers(app)

    # --- Routes ---
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    @app.get("/", include_in_schema=False)
    async def root() -> dict[str, str]:
        return {
            "name": settings.APP_NAME,
            "version": __version__,
            "docs": "/docs",
        }

    return app


app = create_app()