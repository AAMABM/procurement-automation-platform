from datetime import datetime, UTC
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.exceptions import ValidationError
from app.models.goods_receipt import GoodsReceipt
from app.models.invoice import Invoice
from app.models.purchase_order import PurchaseOrder
from app.repositories.base import BaseRepository
from app.schemas.invoice import GRCreate, InvoiceCreate

class GRRepository(BaseRepository[GoodsReceipt]):
    model = GoodsReceipt
    async def get_latest_gr_number(self, year: int) -> str | None:
        stmt = select(GoodsReceipt.gr_number).where(GoodsReceipt.gr_number.like(f"GR-{year}-%")).order_by(GoodsReceipt.gr_number.desc()).limit(1)
        return await self.session.scalar(stmt)

class InvoiceRepository(BaseRepository[Invoice]):
    model = Invoice

class InvoiceService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.grs = GRRepository(session)
        self.invoices = InvoiceRepository(session)

    async def create_gr(self, payload: GRCreate) -> GoodsReceipt:
        po = await self.session.get(PurchaseOrder, payload.po_id)
        if not po: raise ValidationError("PO not found.")
        if po.status != "ISSUED": raise ValidationError("Only ISSUED POs can be received.")
        
        current_year = datetime.now(UTC).year
        latest = await self.grs.get_latest_gr_number(current_year)
        seq = (int(latest.split("-")[-1]) + 1) if latest else 1
        gr_num = f"GR-{current_year}-{seq:05d}"

        gr = GoodsReceipt(gr_number=gr_num, po_id=po.id, received_by=payload.received_by)
        po.status = "FULFILLED"
        self.session.add(gr)
        await self.session.commit()
        await self.session.refresh(gr)
        return gr

    async def create_invoice(self, payload: InvoiceCreate) -> Invoice:
        po = await self.session.get(PurchaseOrder, payload.po_id)
        if not po: raise ValidationError("PO not found.")
        
        # 3-Way Match Logic
        gr = await self.session.scalar(select(GoodsReceipt).where(GoodsReceipt.po_id == po.id))
        
        status = "PENDING_MATCH"
        if gr:
            # If goods are received, compare the amounts.
            if float(po.total_amount) == float(payload.total_amount):
                status = "MATCHED"
                po.status = "CLOSED" # PO is officially done
            else:
                status = "EXCEPTION" # Amount mismatch!
        
        inv = Invoice(
            invoice_number=payload.invoice_number,
            po_id=po.id,
            vendor_id=po.vendor_id,
            total_amount=payload.total_amount,
            currency=po.currency,
            status=status
        )
        self.session.add(inv)
        await self.session.commit()
        await self.session.refresh(inv)
        return inv

    async def list(self) -> list[Invoice]:
        stmt = select(Invoice).where(Invoice.deleted_at.is_(None)).order_by(Invoice.created_at.desc())
        return list((await self.session.execute(stmt)).scalars().all())