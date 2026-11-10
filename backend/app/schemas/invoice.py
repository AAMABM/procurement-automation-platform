from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import Field
from app.schemas.common import ORMModel

class GRCreate(ORMModel):
    po_id: UUID
    received_by: str = Field(..., min_length=2)

class GRResponse(ORMModel):
    id: UUID
    gr_number: str
    po_id: UUID
    received_by: str
    created_at: datetime

class InvoiceCreate(ORMModel):
    po_id: UUID
    invoice_number: str = Field(..., min_length=2)
    total_amount: Decimal = Field(..., gt=0)

class InvoiceResponse(ORMModel):
    id: UUID
    invoice_number: str
    po_id: UUID
    vendor_id: UUID
    total_amount: Decimal
    currency: str
    status: str
    created_at: datetime