"""
Structured access logging + latency tracking.

Why this exists:
    Full-fidelity access logs are the backbone of observability. We log
    method, path, status, duration, and request_id in one line — JSON in prod.

Design:
    - Tracks latency in milliseconds.
    - Skips health probes (they'd drown out real traffic in dashboards).
    - Emits `http_request` events consumed by metrics pipelines.
"""
import time

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = structlog.get_logger("http")

_SKIP_PATHS = {"/health/live", "/health/ready", "/openapi.json", "/docs", "/redoc"}


class AccessLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in _SKIP_PATHS:
            return await call_next(request)

        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start) * 1000, 2)

        logger.info(
            "http_request",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        return response