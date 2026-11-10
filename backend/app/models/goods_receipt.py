"""
Goods Receipt (GR) Model.

Enterprise Decisions:
    - A GR is tied directly to a PO. It proves that physical goods were 
      received and audited by a user.
    - Maps to SAP MSEG (Material Document).
"""
from uuid import UUID
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.mixins import AuditMixin, UUIDPrimaryKeyMixin

class GoodsReceipt(Base, UUIDPrimaryKeyMixin, AuditMixin):
    __tablename__ = "goods_receipts"

    gr_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    po_id: Mapped[UUID] = mapped_column(ForeignKey("purchase_orders.id"), unique=True, nullable=False)
    received_by: Mapped[str] = mapped_column(String(255), nullable=False)

    purchase_order: Mapped["PurchaseOrder"] = relationship("PurchaseOrder", lazy="joined")