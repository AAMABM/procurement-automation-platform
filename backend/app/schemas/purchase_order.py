from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import Field
from app.schemas.common import ORMModel
from app.schemas.vendor import VendorResponse
from app.schemas.requisition import PRLineItemResponse

class POCreate(ORMModel):
    requisition_id: UUID
    vendor_id: UUID

class POLineItemResponse(ORMModel):
    id: UUID
    description: str
    quantity: Decimal
    unit_price: Decimal
    total_price: Decimal
    gl_account: str
    cost_center: str

class POResponse(ORMModel):
    id: UUID
    po_number: str
    requisition_id: UUID | None # <--- Changed to allow None
    vendor_id: UUID
    status: str
    total_amount: Decimal
    currency: str
    created_at: datetime
    vendor: VendorResponse
    line_items: list[POLineItemResponse]