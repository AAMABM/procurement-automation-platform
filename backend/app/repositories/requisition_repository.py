from uuid import UUID
from sqlalchemy import select
from app.models.requisition import PurchaseRequisition
from app.repositories.base import BaseRepository

class PRRepository(BaseRepository[PurchaseRequisition]):
    model = PurchaseRequisition

    async def get_latest_pr_number_for_year(self, year: int) -> str | None:
        """Finds the most recent PR number for the given year to generate the next sequence."""
        prefix = f"PR-{year}-"
        stmt = (
            select(PurchaseRequisition.pr_number)
            .where(PurchaseRequisition.pr_number.like(f"{prefix}%"))
            .order_by(PurchaseRequisition.pr_number.desc())
            .limit(1)
        )
        return await self.session.scalar(stmt)

    async def list_by_requester(self, requester_id: UUID) -> list[PurchaseRequisition]:
        stmt = (
            select(PurchaseRequisition)
            .where(
                PurchaseRequisition.requester_id == requester_id,
                PurchaseRequisition.deleted_at.is_(None)
            )
            .order_by(PurchaseRequisition.created_at.desc())
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def list_all(self) -> list[PurchaseRequisition]:
        stmt = (
            select(PurchaseRequisition)
            .where(PurchaseRequisition.deleted_at.is_(None))
            .order_by(PurchaseRequisition.created_at.desc())
        )
        return list((await self.session.execute(stmt)).scalars().all())