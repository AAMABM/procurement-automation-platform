"""
Structured logging.

Why this exists:
    Enterprise apps require machine-parseable logs for SIEM ingestion
    (Splunk, Datadog, ELK). Structured JSON logs make filtering, alerting,
    and correlation by request_id trivial.

Enterprise decisions:
    - `structlog` — supports both human-readable console (dev) and JSON (prod).
    - Request ID is bound to context via `contextvars` (async-safe).
    - No PII in logs: hashing of emails is done at call site.
    - Uvicorn's default logger is intercepted so access logs share the same
      format and correlation IDs.

SAP S/4HANA relevance:
    Replaces SM21/ST11 log viewing with modern observability. Enterprise
    audit (ITGC) requires request attribution — bind `user_id` to context
    after authentication.
"""
import logging
import sys

import structlog

from app.core.config import get_settings


def configure_logging() -> None:
    settings = get_settings()

    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
    ]

    if settings.LOG_FORMAT == "json":
        renderer: structlog.types.Processor = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.processors.format_exc_info,
            renderer,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Bridge stdlib logging (uvicorn, sqlalchemy) through structlog
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            processor=renderer,
            foreign_pre_chain=shared_processors,
        )
    )
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(settings.LOG_LEVEL)

    # Tame noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.DEBUG else logging.WARNING
    )


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    return structlog.get_logger(name) if name else structlog.get_logger()