"""
Invoice Model.

Enterprise Decisions:
    - `invoice_number` is the vendor's external reference (e.g., INV-2026-99).
    - `status` tracks the 3-way match result (PENDING_MATCH, MATCHED, EXCEPTION).
    - Maps to SAP RBKP (Invoice Document Header).
"""
from uuid import UUID
from decimal import Decimal
from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.mixins import AuditMixin, SoftDeleteMixin, UUIDPrimaryKeyMixin

class Invoice(Base, UUIDPrimaryKeyMixin, AuditMixin, SoftDeleteMixin):
    __tablename__ = "invoices"

    invoice_number: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    po_id: Mapped[UUID] = mapped_column(ForeignKey("purchase_orders.id"), nullable=False)
    vendor_id: Mapped[UUID] = mapped_column(ForeignKey("vendors.id"), nullable=False)
    
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    
    # PENDING_MATCH, MATCHED, EXCEPTION
    status: Mapped[str] = mapped_column(String(20), default="PENDING_MATCH", nullable=False)

    purchase_order: Mapped["PurchaseOrder"] = relationship("PurchaseOrder", lazy="joined")