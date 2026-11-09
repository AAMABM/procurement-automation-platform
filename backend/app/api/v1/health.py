"""
Health & readiness endpoints.

- `/health/live`  — process is up (used by liveness probe).
- `/health/ready` — DB reachable (used by readiness probe / LB).

Why split:
    Kubernetes must distinguish "process alive" from "ready to serve traffic".
    Merging them causes cascading restarts during rolling deploys.

SAP S/4HANA relevance:
    Mirrors SAP's `/sap/public/ping` and `/sap/public/bc/ping` health checks.
"""
from fastapi import APIRouter, status
from sqlalchemy import text

from app.api.deps import DB
from app.core.config import get_settings

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/live", status_code=status.HTTP_200_OK)
async def liveness() -> dict[str, str]:
    return {"status": "alive"}


@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness(session: DB) -> dict[str, str]:
    settings = get_settings()
    await session.execute(text("SELECT 1"))
    return {"status": "ready", "env": settings.APP_ENV}