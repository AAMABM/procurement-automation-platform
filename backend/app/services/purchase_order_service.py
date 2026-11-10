"""
Purchase Order Service.
Handles the conversion of an APPROVED PR into a PO.
"""
from datetime import datetime, UTC
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.exceptions import ValidationError
from app.models.purchase_order import PurchaseOrder, POLineItem
from app.models.vendor import Vendor
from app.repositories.base import BaseRepository
from app.models.requisition import PurchaseRequisition
from app.schemas.purchase_order import POCreate
from app.services.sap_integration_service import SAPIntegrationService

class PORepository(BaseRepository[PurchaseOrder]):
    model = PurchaseOrder

    async def get_latest_po_number_for_year(self, year: int) -> str | None:
        prefix = f"PO-{year}-"
        stmt = (
            select(PurchaseOrder.po_number)
            .where(PurchaseOrder.po_number.like(f"{prefix}%"))
            .order_by(PurchaseOrder.po_number.desc())
            .limit(1)
        )
        return await self.session.scalar(stmt)

class POService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.pos = PORepository(session)

    async def list(self) -> list[PurchaseOrder]:
        """Fetches all POs for the UI."""
        stmt = (
            select(PurchaseOrder)
            .where(PurchaseOrder.deleted_at.is_(None))
            .order_by(PurchaseOrder.created_at.desc())
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def create_from_pr(self, payload: POCreate) -> PurchaseOrder:
        # 1. Verify PR exists and is APPROVED
        pr = await self.session.get(PurchaseRequisition, payload.requisition_id)
        if not pr:
            raise ValidationError("Purchase Requisition not found.")
        if pr.status != "APPROVED":
            raise ValidationError("Only APPROVED requisitions can be converted to a PO.")
        
        # 2. Check if PR is already converted
        existing_po = await self.pos.get_by(requisition_id=pr.id)
        if existing_po:
            raise ValidationError("A Purchase Order already exists for this Requisition.")

        # 3. Verify Vendor exists and is ACTIVE
        vendor = await self.session.get(Vendor, payload.vendor_id)
        if not vendor:
            raise ValidationError("Vendor not found.")
        if vendor.status != "ACTIVE":
            raise ValidationError("Cannot issue a PO to a BLOCKED or INACTIVE vendor.")

        # 4. Generate PO Number
        current_year = datetime.now(UTC).year
        latest_po = await self.pos.get_latest_po_number_for_year(current_year)
        seq = (int(latest_po.split("-")[-1]) + 1) if latest_po else 1
        po_num = f"PO-{current_year}-{seq:05d}"

        # 5. Create PO Line Items (Snapshot from PR)
        po_line_items = []
        for item in pr.line_items:
            po_line_items.append(
                POLineItem(
                    description=item.description,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    total_price=item.total_price,
                    gl_account=item.gl_account,
                    cost_center=item.cost_center
                )
            )

        po = PurchaseOrder(
            po_number=po_num,
            requisition_id=pr.id,
            vendor_id=vendor.id,
            status="ISSUED",
            total_amount=pr.total_amount,
            currency=pr.currency,
            line_items=po_line_items
        )

        await self.pos.add(po)
        await self.session.commit()
        await self.session.refresh(po)

        # Trigger SAP S/4HANA Integration
        sap_service = SAPIntegrationService(self.session)
        await sap_service.sync_po_to_sap(po, vendor.name)

        return po