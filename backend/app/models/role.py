"""
Role + Permission entities (RBAC).

Design:
    User <--M:N--> Role <--M:N--> Permission

    This is the classic **NIST RBAC** model and matches SAP's
    Users → Roles → Authorization Objects hierarchy. Roles are logical
    (e.g., "procurement_manager"); permissions are atomic (e.g.,
    "purchase_orders:approve").

    `is_system_role` protects seeded roles from deletion via API — the
    platform must always have working admin access even after user error.

Tradeoff:
    Deeper ABAC (e.g., "approve POs under $10K in your cost center") will
    come later as a separate policy engine — RBAC is the necessary substrate
    and enforces *what* actions are allowed; ABAC will enforce *on which
    instances*. Mixing them now would produce the worst of both worlds.
"""
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, ForeignKey, String, Table, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import AuditMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.user import User


# Association tables — no extra payload; pure M:N join.
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column(
        "user_id",
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "role_id",
        PGUUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column(
        "role_id",
        PGUUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "permission_id",
        PGUUID(as_uuid=True),
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Permission(Base, UUIDPrimaryKeyMixin, AuditMixin):
    __tablename__ = "permissions"

    code: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)

    def __repr__(self) -> str:
        return f"<Permission code={self.code}>"


class Role(Base, UUIDPrimaryKeyMixin, AuditMixin):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    is_system_role: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    users: Mapped[list["User"]] = relationship(
        "User", secondary=user_roles, back_populates="roles"
    )
    permissions: Mapped[list[Permission]] = relationship(
        "Permission", secondary=role_permissions, lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Role name={self.name}>"