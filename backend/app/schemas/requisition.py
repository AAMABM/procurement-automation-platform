from datetime import date, datetime
from decimal import Decimal
from uuid import UUID
from pydantic import Field
from app.schemas.common import ORMModel

class PRLineItemCreate(ORMModel):
    description: str = Field(..., min_length=2)
    quantity: Decimal = Field(..., gt=0)
    unit_price: Decimal = Field(..., ge=0)
    gl_account: str = Field(..., min_length=2)
    cost_center: str = Field(..., min_length=2)

class PRLineItemResponse(ORMModel):
    id: UUID
    description: str
    quantity: Decimal
    unit_price: Decimal
    total_price: Decimal
    gl_account: str
    cost_center: str

class PRCreate(ORMModel):
    title: str = Field(..., min_length=3)
    currency: str = Field(default="USD", max_length=3)
    justification: str | None = None
    required_by: date | None = None
    line_items: list[PRLineItemCreate] = Field(..., min_length=1)

class PRResponse(ORMModel):
    id: UUID
    pr_number: str
    title: str
    status: str
    total_amount: Decimal
    currency: str
    justification: str | None
    required_by: date | None
    requester_id: UUID
    created_at: datetime
    line_items: list[PRLineItemResponse]