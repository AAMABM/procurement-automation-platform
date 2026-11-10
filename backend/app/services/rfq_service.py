from datetime import datetime, UTC
from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.exceptions import ValidationError
from app.models.rfq import RFQ, RFQInvitation, Quotation, QuotationLineItem
from app.models.purchase_order import PurchaseOrder, POLineItem
from app.models.vendor import Vendor
from app.repositories.rfq_repository import RFQRepository
from app.schemas.rfq import RFQCreate, QuotationCreate

class RFQService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.rfqs = RFQRepository(session)

    async def list(self) -> list[RFQ]:
        return await self.rfqs.list_all()

    async def create(self, payload: RFQCreate) -> RFQ:
        current_year = datetime.now(UTC).year
        latest = await self.rfqs.get_latest_rfq_number_for_year(current_year)
        seq = (int(latest.split("-")[-1]) + 1) if latest else 1
        rfq_num = f"RFQ-{current_year}-{seq:05d}"

        # Validate vendors
        vendors = (await self.session.execute(select(Vendor).where(Vendor.id.in_(payload.vendor_ids)))).scalars().all()
        if len(vendors) != len(set(payload.vendor_ids)):
            raise ValidationError("One or more vendor IDs are invalid.")

        rfq = RFQ(
            rfq_number=rfq_num,
            title=payload.title,
            deadline=payload.deadline,
            status="PUBLISHED",
        )
        self.session.add(rfq)
        await self.session.flush()

        for vendor in vendors:
            self.session.add(RFQInvitation(rfq_id=rfq.id, vendor_id=vendor.id))

        await self.session.commit()
        await self.session.refresh(rfq)
        return rfq

    async def submit_quotation(self, rfq_id: UUID, payload: QuotationCreate) -> Quotation:
        rfq = await self.session.get(RFQ, rfq_id)
        if not rfq or rfq.status not in ["PUBLISHED", "EVALUATION"]:
            raise ValidationError("RFQ not available for quotations.")

        total_amount = sum((item.quantity * item.unit_price for item in payload.line_items), Decimal("0.00"))
        
        quotation = Quotation(
            rfq_id=rfq.id,
            vendor_id=payload.vendor_id,
            total_amount=total_amount,
            lead_time_days=payload.lead_time_days,
            status="RECEIVED"
        )
        self.session.add(quotation)
        await self.session.flush()

        for item in payload.line_items:
            self.session.add(QuotationLineItem(
                quotation_id=quotation.id,
                description=item.description,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total_price=item.quantity * item.unit_price
            ))

        rfq.status = "EVALUATION"
        
        # Update invitation status
        for inv in rfq.invitations:
            if inv.vendor_id == payload.vendor_id:
                inv.status = "RESPONDED"

        await self.session.commit()
        await self.session.refresh(quotation)
        return quotation

    async def award_quotation(self, rfq_id: UUID, quotation_id: UUID) -> PurchaseOrder:
        """Selects the winning quote, rejects others, and auto-generates the PO."""
        rfq = await self.session.get(RFQ, rfq_id)
        if not rfq or rfq.status != "EVALUATION":
            raise ValidationError("RFQ must be in EVALUATION status to award.")

        winning_quote = await self.session.get(Quotation, quotation_id)
        if not winning_quote or winning_quote.rfq_id != rfq.id:
            raise ValidationError("Invalid quotation.")

        # 1. Mark statuses
        winning_quote.status = "AWARDED"
        for q in rfq.quotations:
            if q.id != winning_quote.id:
                q.status = "REJECTED"
        rfq.status = "AWARDED"

        # 2. Generate PO (Snapshot quotation items)
        current_year = datetime.now(UTC).year
        latest_po = await self.session.scalar(
            select(PurchaseOrder.po_number).where(PurchaseOrder.po_number.like(f"PO-{current_year}-%")).order_by(PurchaseOrder.po_number.desc()).limit(1)
        )
        seq = (int(latest_po.split("-")[-1]) + 1) if latest_po else 1
        po_num = f"PO-{current_year}-{seq:05d}"

        po_line_items = []
        for item in winning_quote.line_items:
            po_line_items.append(
                POLineItem(
                    description=item.description,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    total_price=item.total_price,
                    gl_account="400100", # Default GL for now
                    cost_center="CC-100"
                )
            )

        po = PurchaseOrder(
            po_number=po_num,
            requisition_id=rfq.pr_id, # Might be null if standalone RFQ
            vendor_id=winning_quote.vendor_id,
            status="ISSUED",
            total_amount=winning_quote.total_amount,
            currency="USD",
            line_items=po_line_items
        )

        self.session.add(po)
        await self.session.commit()
        await self.session.refresh(po)
        
        # Trigger SAP Sync here later (Phase 5 adapter)
        return po