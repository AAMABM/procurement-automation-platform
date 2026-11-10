"""
Purchase Order (PO) Models.

Enterprise Decisions:
    - POs are generated strictly from APPROVED PRs.
    - We copy the line items from the PR to the PO. This creates a historical 
      snapshot so that if the PR is ever edited or deleted, the PO remains 
      an accurate record of what was ordered.
    - Tied to a Vendor via `vendor_id`.

SAP S/4HANA Relevance:
    Maps to table EKKO (PO Header) and EKPO (PO Items).
    PO Number acts like SAP's EBELN.
"""
from typing import TYPE_CHECKING
from uuid import UUID
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import AuditMixin, SoftDeleteMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.requisition import PurchaseRequisition
    from app.models.vendor import Vendor

class PurchaseOrder(Base, UUIDPrimaryKeyMixin, AuditMixin, SoftDeleteMixin):
    __tablename__ = "purchase_orders"

    po_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    
    # A PR can only be converted to ONE PO. 
    requisition_id: Mapped[UUID] = mapped_column(
        ForeignKey("purchase_requisitions.id", ondelete="RESTRICT"), unique=True, nullable=False
    )
    vendor_id: Mapped[UUID] = mapped_column(
        ForeignKey("vendors.id", ondelete="RESTRICT"), nullable=False
    )
    
    status: Mapped[str] = mapped_column(String(20), default="ISSUED", nullable=False, index=True)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)

    # Relationships
    requisition: Mapped["PurchaseRequisition"] = relationship("PurchaseRequisition", lazy="joined")
    vendor: Mapped["Vendor"] = relationship("Vendor", lazy="joined")
    line_items: Mapped[list["POLineItem"]] = relationship(
        "POLineItem", back_populates="purchase_order", cascade="all, delete-orphan", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<PO {self.po_number} - {self.status}>"

class POLineItem(Base, UUIDPrimaryKeyMixin, AuditMixin):
    __tablename__ = "po_line_items"

    po_id: Mapped[UUID] = mapped_column(
        ForeignKey("purchase_orders.id", ondelete="CASCADE"), nullable=False
    )
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    total_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    
    gl_account: Mapped[str] = mapped_column(String(50), nullable=False)
    cost_center: Mapped[str] = mapped_column(String(50), nullable=False)

    purchase_order: Mapped["PurchaseOrder"] = relationship("PurchaseOrder", back_populates="line_items")