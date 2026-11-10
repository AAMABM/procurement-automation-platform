from decimal import Decimal
from pydantic import BaseModel

class VendorSpend(BaseModel):
    vendor_name: str
    total_spend: Decimal

class DashboardStats(BaseModel):
    total_spend: Decimal
    active_pos: int
    pending_requisitions: int
    exception_rate: float
    rfq_response_rate: float
    spend_by_vendor: list[VendorSpend]