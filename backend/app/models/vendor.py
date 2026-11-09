"""
Vendor Master Data.

Enterprise Decisions:
    - `sap_vendor_number` is unique and nullable. If a company is migrating
      from S/4HANA, they already have vendor numbers (e.g., '0000100045').
      Newly created vendors will get this populated during Phase 6 integration.
    - We use a soft-block strategy (`status = BLOCKED`) rather than deleting.
      Procurement history must remain intact for audit (SOX compliance).

SAP S/4HANA Relevance:
    Maps to table LFA1 (General Data) and LFM1 (Purchasing Organization Data).
"""
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import AuditMixin, SoftDeleteMixin, UUIDPrimaryKeyMixin


class Vendor(Base, UUIDPrimaryKeyMixin, AuditMixin, SoftDeleteMixin):
    __tablename__ = "vendors"

    sap_vendor_number: Mapped[str | None] = mapped_column(
        String(20), unique=True, index=True, nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    tax_id: Mapped[str] = mapped_column(String(50), nullable=False)
    contact_email: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # 'ACTIVE', 'BLOCKED', 'INACTIVE'
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", nullable=False)

    def __repr__(self) -> str:
        return f"<Vendor {self.name} ({self.sap_vendor_number})>"