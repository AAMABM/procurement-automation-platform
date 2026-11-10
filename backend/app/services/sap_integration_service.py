import json
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.integration_log import IntegrationLog
from app.models.purchase_order import PurchaseOrder

class SAPIntegrationService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        # In production, this URL comes from env vars (e.g., SAP BTP Destination)
        self.sap_url = "http://localhost:8000/api/v1/mock-sap/odata/PurchaseOrder"

    async def sync_po_to_sap(self, po: PurchaseOrder, vendor_name: str) -> None:
        """Fires an async HTTP call to SAP and logs the result."""
        
        # 1. Build the OData Payload
        payload = {
            "CompanyCode": "1000", # Standard SAP Company Code
            "Vendor": po.vendor_id.hex[:10], # Simulating SAP Vendor ID
            "TotalAmount": float(po.total_amount),
            "Currency": po.currency
        }
        payload_str = json.dumps(payload)

        # 2. Send to SAP (Mock)
        status = "FAILED"
        response_text = None
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.sap_url, json=payload)
                response_text = response.text
                if response.status_code == 200:
                    status = "SUCCESS"
        except Exception as e:
            response_text = str(e)

        # 3. Log the result in the database
        log = IntegrationLog(
            po_id=po.id,
            target_system="SAP_S4HANA",
            status=status,
            payload=payload_str,
            response=response_text
        )
        self.session.add(log)
        await self.session.commit()