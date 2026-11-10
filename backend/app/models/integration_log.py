"""
Integration Log Model.

Enterprise Decisions:
    - Every outbound call to SAP must be logged for audit and troubleshooting.
    - Stores the exact JSON payload sent and the response received.

SAP S/4HANA Relevance:
    - Equivalent to SAP's IDoc monitoring (WE02/WE05) or the 
      SAP Gateway Error Log (/IWFND/ERROR_LOG).
"""
from uuid import UUID
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from app.models.mixins import AuditMixin, UUIDPrimaryKeyMixin

class IntegrationLog(Base, UUIDPrimaryKeyMixin, AuditMixin):
    __tablename__ = "integration_logs"

    po_id: Mapped[UUID] = mapped_column(ForeignKey("purchase_orders.id", ondelete="CASCADE"), nullable=False)
    target_system: Mapped[str] = mapped_column(String(50), default="SAP_S4HANA", nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False) # SUCCESS, FAILED
    
    payload: Mapped[str] = mapped_column(Text, nullable=False)
    response: Mapped[str | None] = mapped_column(Text, nullable=True)