"""
Purchase Requisition (PR) and Line Items.

Enterprise Decisions:
    - PR status is a string enum (not a PostgreSQL ENUM) to allow easy
      workflow expansions without locking the DB schema.
    - Line items track `gl_account` and `cost_center`. These are critical 
      for SAP integration and financial reporting.

SAP S/4HANA Relevance:
    Maps to table EBAN (Purchase Requisition). Line items map to EBAN items.
"""
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import AuditMixin, SoftDeleteMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.user import User


class PurchaseRequisition(Base, UUIDPrimaryKeyMixin, AuditMixin, SoftDeleteMixin):
    __tablename__ = "purchase_requisitions"

    pr_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    requester_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    # 'DRAFT', 'SUBMITTED', 'APPROVED', 'REJECTED', 'CANCELLED'
    status: Mapped[str] = mapped_column(String(20), default="DRAFT", nullable=False, index=True)
    
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0.00, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    justification: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    required_by: Mapped[date | None] = mapped_column(nullable=True)

    requester: Mapped["User"] = relationship("User", lazy="joined")
    line_items: Mapped[list["PRLineItem"]] = relationship(
        "PRLineItem", back_populates="requisition", cascade="all, delete-orphan", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<PR {self.pr_number} - {self.status}>"


class PRLineItem(Base, UUIDPrimaryKeyMixin, AuditMixin):
    __tablename__ = "pr_line_items"

    requisition_id: Mapped[UUID] = mapped_column(
        ForeignKey("purchase_requisitions.id", ondelete="CASCADE"), nullable=False
    )
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    total_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    
    gl_account: Mapped[str] = mapped_column(String(50), nullable=False)
    cost_center: Mapped[str] = mapped_column(String(50), nullable=False)

    requisition: Mapped["PurchaseRequisition"] = relationship(
        "PurchaseRequisition", back_populates="line_items"
    )