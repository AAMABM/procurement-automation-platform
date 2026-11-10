from fastapi import APIRouter
from pydantic import BaseModel
import uuid

router = APIRouter(prefix="/mock-sap", tags=["Mock SAP S/4HANA"])

class SAPODataPayload(BaseModel):
    CompanyCode: str
    Vendor: str
    TotalAmount: float
    Currency: str

@router.post("/odata/PurchaseOrder")
async def receive_sap_po(payload: SAPODataPayload):
    """
    Simulates SAP S/4HANA receiving an OData POST request.
    Returns a fake SAP Document Number (EBELN).
    """
    # Generate a fake 10-digit SAP PO number (e.g., 4500000123)
    sap_po_number = f"45{uuid.uuid4().int % 100000000:08d}"
    
    return {
        "d": {
            "PurchaseOrder": sap_po_number,
            "Message": "Purchase Order created successfully in S/4HANA",
            "Status": "S"
        }
    }