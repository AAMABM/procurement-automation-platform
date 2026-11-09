"""
Reusable ORM mixins.

Why this exists:
    UUID primary keys and audit columns are repeated across every entity.
    Mixins eliminate copy-paste bugs and ensure consistent semantics.

Why UUID PKs?
    - Non-enumerable — safer in public APIs.
    - Merge-friendly for future multi-region / data migration scenarios.
    - SAP S/4HANA uses GUIDs for many entities; alignment eases integration.

Why timezone-aware timestamps?
    Enterprise deployments span time zones; naive timestamps cause silent bugs.
"""
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column


class UUIDPrimaryKeyMixin:
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid4
    )


class AuditMixin:
    """created_at/updated_at + who did it. `updated_by` set by service layer."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    """
    Soft delete preserves audit trails — required by SOX for financial systems.
    Queries explicitly filter `deleted_at IS NULL` in repositories.
    """

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )