"""
RFQ and Quotation Models.

Enterprise Decisions:
    - An RFQ can be linked to an APPROVED PR (sourcing a specific requirement).
    - Multiple Vendors are invited via `RFQInvitation`.
    - Vendors respond with `Quotation` headers and `QuotationLineItem` details.
    - Statuses track the state machine: DRAFT -> PUBLISHED -> EVALUATION -> AWARDED.

SAP S/4HANA Relevance:
    - Maps to SAP's Sourcing module (Ariba Sourcing) and standard RFQ documents.
    - The winning Quotation drives the Purchase Order creation.
"""
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import AuditMixin, SoftDeleteMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.requisition import PurchaseRequisition
    from app.models.vendor import Vendor

class RFQ(Base, UUIDPrimaryKeyMixin, AuditMixin, SoftDeleteMixin):
    __tablename__ = "rfqs"

    rfq_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    pr_id: Mapped[UUID | None] = mapped_column(ForeignKey("purchase_requisitions.id"), nullable=True)
    
    # DRAFT, PUBLISHED, EVALUATION, AWARDED, CANCELLED
    status: Mapped[str] = mapped_column(String(20), default="DRAFT", nullable=False)
    deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    requisition: Mapped["PurchaseRequisition"] = relationship("PurchaseRequisition", lazy="joined")
    invitations: Mapped[list["RFQInvitation"]] = relationship("RFQInvitation", back_populates="rfq", cascade="all, delete-orphan", lazy="selectin")
    quotations: Mapped[list["Quotation"]] = relationship("Quotation", back_populates="rfq", cascade="all, delete-orphan", lazy="selectin")


class RFQInvitation(Base, UUIDPrimaryKeyMixin, AuditMixin):
    __tablename__ = "rfq_invitations"

    rfq_id: Mapped[UUID] = mapped_column(ForeignKey("rfqs.id", ondelete="CASCADE"), nullable=False)
    vendor_id: Mapped[UUID] = mapped_column(ForeignKey("vendors.id"), nullable=False)
    
    # INVITED, RESPONDED, DECLINED
    status: Mapped[str] = mapped_column(String(20), default="INVITED", nullable=False)

    rfq: Mapped["RFQ"] = relationship("RFQ", back_populates="invitations")
    vendor: Mapped["Vendor"] = relationship("Vendor", lazy="joined")


class Quotation(Base, UUIDPrimaryKeyMixin, AuditMixin):
    __tablename__ = "quotations"

    rfq_id: Mapped[UUID] = mapped_column(ForeignKey("rfqs.id", ondelete="CASCADE"), nullable=False)
    vendor_id: Mapped[UUID] = mapped_column(ForeignKey("vendors.id"), nullable=False)
    
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    lead_time_days: Mapped[int] = mapped_column(nullable=False)
    
    # RECEIVED, AWARDED, REJECTED
    status: Mapped[str] = mapped_column(String(20), default="RECEIVED", nullable=False)

    rfq: Mapped["RFQ"] = relationship("RFQ", back_populates="quotations")
    vendor: Mapped["Vendor"] = relationship("Vendor", lazy="joined")
    line_items: Mapped[list["QuotationLineItem"]] = relationship("QuotationLineItem", back_populates="quotation", cascade="all, delete-orphan", lazy="selectin")


class QuotationLineItem(Base, UUIDPrimaryKeyMixin, AuditMixin):
    __tablename__ = "quotation_line_items"

    quotation_id: Mapped[UUID] = mapped_column(ForeignKey("quotations.id", ondelete="CASCADE"), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    total_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    quotation: Mapped["Quotation"] = relationship("Quotation", back_populates="line_items")