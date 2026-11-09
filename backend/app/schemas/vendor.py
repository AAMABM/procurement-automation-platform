from datetime import datetime
from uuid import UUID
from pydantic import EmailStr, Field
from app.schemas.common import ORMModel

class VendorCreate(ORMModel):
    name: str = Field(..., min_length=2, max_length=255)
    tax_id: str = Field(..., min_length=2, max_length=50)
    contact_email: EmailStr
    sap_vendor_number: str | None = None

class VendorResponse(ORMModel):
    id: UUID
    name: str
    tax_id: str
    contact_email: EmailStr
    sap_vendor_number: str | None
    status: str
    created_at: datetime