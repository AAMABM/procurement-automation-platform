"""
User entity.

Design:
    - `email` is unique + indexed (login handle).
    - `hashed_password` is excluded from repr and serialization.
    - `roles` — many-to-many; a user may hold multiple roles (e.g., buyer + auditor).
    - `is_superuser` bypasses permission checks (SAP "SAP_ALL").
    - `is_active` allows disabling without deleting (retains audit trail).
    - `last_login_at` — required for inactive-user reporting in regulated orgs.

SAP S/4HANA relevance:
    Maps to SAP User Master Record (SU01). `is_superuser` ≈ SAP_ALL profile.
    `is_active` ≈ "User Locked" status. The audit fields support GRC
    Access Control reviews.
"""
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import AuditMixin, SoftDeleteMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.role import Role


class User(Base, UUIDPrimaryKeyMixin, AuditMixin, SoftDeleteMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    roles: Mapped[list["Role"]] = relationship(
        "Role",
        secondary="user_roles",
        back_populates="users",
        lazy="selectin",       # eager-load avoids N+1 on token issuance
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"

    @property
    def permission_codes(self) -> set[str]:
        """Union of permissions across all roles. Superuser => wildcard."""
        if self.is_superuser:
            return {"*"}
        perms: set[str] = set()
        for role in self.roles:
            for perm in role.permissions:
                perms.add(perm.code)
        return perms