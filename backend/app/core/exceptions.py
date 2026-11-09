"""
Domain exception hierarchy + global handlers.

Why this exists:
    Business errors (e.g., "email already registered") must be distinguishable
    from technical errors (e.g., database down). Centralizing translation
    to HTTP responses ensures consistency across every endpoint.

Enterprise decisions:
    - Custom exceptions inherit from a common `AppException` with an error code.
    - API responses follow RFC 7807 (Problem Details) shape.
    - Internal exception details are never leaked to clients; a correlation ID
      is returned instead.

SAP S/4HANA relevance:
    Aligns with SAP's standardized error message structure
    ({ "error": { "code": "...", "message": "...", "target": "..." } }) so
    third-party integrations can parse errors uniformly.
"""
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import get_logger

logger = get_logger(__name__)


class AppException(Exception):
    """Base class for all domain exceptions."""

    status_code: int = status.HTTP_400_BAD_REQUEST
    code: str = "application_error"
    message: str = "An application error occurred."

    def __init__(
        self,
        message: str | None = None,
        *,
        code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message or self.message)
        if message:
            self.message = message
        if code:
            self.code = code
        self.details = details or {}


class AuthenticationError(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "authentication_error"
    message = "Authentication failed."


class AuthorizationError(AppException):
    status_code = status.HTTP_403_FORBIDDEN
    code = "authorization_error"
    message = "You do not have permission to perform this action."


class NotFoundError(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    code = "not_found"
    message = "Resource not found."


class ConflictError(AppException):
    status_code = status.HTTP_409_CONFLICT
    code = "conflict"
    message = "Resource already exists."


class ValidationError(AppException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    code = "validation_error"
    message = "Validation failed."


def _problem_response(
    *,
    status_code: int,
    code: str,
    message: str,
    details: dict[str, Any] | None,
    request: Request,
) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None)
    body: dict[str, Any] = {
        "error": {
            "code": code,
            "message": message,
            "request_id": request_id,
        }
    }
    if details:
        body["error"]["details"] = details
    if request_id:
        body["error"]["trace_id"] = request_id
    return JSONResponse(status_code=status_code, content=body)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def _app_exception(request: Request, exc: AppException) -> JSONResponse:
        logger.warning(
            "app_exception",
            code=exc.code,
            message=exc.message,
            details=exc.details,
        )
        return _problem_response(
            status_code=exc.status_code,
            code=exc.code,
            message=exc.message,
            details=exc.details,
            request=request,
        )

    @app.exception_handler(RequestValidationError)
    async def _validation(request: Request, exc: RequestValidationError) -> JSONResponse:
        return _problem_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code="validation_error",
            message="Request validation failed.",
            details={"errors": exc.errors()},
            request=request,
        )

    @app.exception_handler(StarletteHTTPException)
    async def _http(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        return _problem_response(
            status_code=exc.status_code,
            code="http_error",
            message=str(exc.detail),
            details=None,
            request=request,
        )

    @app.exception_handler(Exception)
    async def _unhandled(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled_exception")
        return _problem_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="internal_error",
            message="An unexpected error occurred. Please contact support with the trace_id.",
            details=None,
            request=request,
        )
