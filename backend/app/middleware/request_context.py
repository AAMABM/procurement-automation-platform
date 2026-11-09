"""
Binds a request-scoped `request_id` to logging context + response header.

Why this exists:
    Correlating a user's reported error back to logs requires an ID
    that travels from browser → API → DB → logs. `X-Request-ID` is the
    industry convention (Envoy, Spring, SAP BTP all honor it).

Design:
    - If the client supplies `X-Request-ID`, we honor it (distributed tracing).
    - Otherwise we generate a UUIDv4.
    - The ID is stored on `request.state` AND in structlog contextvars, so
      every log line within the request automatically carries it.
"""
import uuid

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response