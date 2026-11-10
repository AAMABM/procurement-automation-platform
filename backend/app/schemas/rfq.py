from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import Field
from app.schemas.common import ORMModel
from app.schemas.vendor import VendorResponse

class RFQInvitationResponse(ORMModel):
    id: UUID
    vendor_id: UUID
    status: str
    vendor: VendorResponse

class QuotationLineItemCreate(ORMModel):
    description: str
    quantity: Decimal
    unit_price: Decimal

class QuotationLineItemResponse(ORMModel):
    id: UUID
    description: str
    quantity: Decimal
    unit_price: Decimal
    total_price: Decimal

class QuotationCreate(ORMModel):
    vendor_id: UUID
    lead_time_days: int
    line_items: list[QuotationLineItemCreate]

class QuotationResponse(ORMModel):
    id: UUID
    vendor_id: UUID
    total_amount: Decimal
    lead_time_days: int
    status: str
    vendor: VendorResponse
    line_items: list[QuotationLineItemResponse]

class RFQCreate(ORMModel):
    title: str
    deadline: datetime
    vendor_ids: list[UUID] = Field(..., min_length=1)

class RFQResponse(ORMModel):
    id: UUID
    rfq_number: str
    title: str
    status: str
    deadline: datetime
    invitations: list[RFQInvitationResponse]
    quotations: list[QuotationResponse]

class AwardQuotation(ORMModel):
    quotation_id: UUID