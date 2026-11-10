from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.purchase_order import PurchaseOrder
from app.models.vendor import Vendor
from app.models.requisition import PurchaseRequisition
from app.models.invoice import Invoice
from app.models.rfq import RFQInvitation, Quotation
from app.schemas.analytics import DashboardStats, VendorSpend

class AnalyticsService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_dashboard_stats(self) -> DashboardStats:
        total_spend = await self.session.scalar(
            select(func.sum(PurchaseOrder.total_amount))
            .where(PurchaseOrder.status.in_(["ISSUED", "FULFILLED", "CLOSED"]))
        ) or 0.00

        active_pos = await self.session.scalar(
            select(func.count(PurchaseOrder.id)).where(PurchaseOrder.status == "ISSUED")
        ) or 0

        pending_reqs = await self.session.scalar(
            select(func.count(PurchaseRequisition.id)).where(PurchaseRequisition.status == "SUBMITTED")
        ) or 0

        total_invoices = await self.session.scalar(select(func.count(Invoice.id))) or 0
        exception_invoices = await self.session.scalar(
            select(func.count(Invoice.id)).where(Invoice.status == "EXCEPTION")
        ) or 0
        exception_rate = (exception_invoices / total_invoices * 100) if total_invoices > 0 else 0.0

        total_invites = await self.session.scalar(select(func.count(RFQInvitation.id))) or 0
        total_quotes = await self.session.scalar(select(func.count(Quotation.id))) or 0
        rfq_response_rate = (total_quotes / total_invites * 100) if total_invites > 0 else 0.0

        vendor_spend_stmt = (
            select(Vendor.name, func.sum(PurchaseOrder.total_amount).label("total_spend"))
            .join(PurchaseOrder, PurchaseOrder.vendor_id == Vendor.id)
            .group_by(Vendor.name)
            .order_by(func.sum(PurchaseOrder.total_amount).desc())
            .limit(5)
        )
        vendor_spend_rows = (await self.session.execute(vendor_spend_stmt)).all()
        spend_by_vendor = [VendorSpend(vendor_name=row[0], total_spend=row[1]) for row in vendor_spend_rows]

        return DashboardStats(
            total_spend=total_spend,
            active_pos=active_pos,
            pending_requisitions=pending_reqs,
            exception_rate=round(exception_rate, 2),
            rfq_response_rate=round(rfq_response_rate, 2),
            spend_by_vendor=spend_by_vendor
        )