from sqlalchemy import select
from app.models.rfq import RFQ
from app.repositories.base import BaseRepository

class RFQRepository(BaseRepository[RFQ]):
    model = RFQ

    async def get_latest_rfq_number_for_year(self, year: int) -> str | None:
        prefix = f"RFQ-{year}-"
        stmt = (
            select(RFQ.rfq_number)
            .where(RFQ.rfq_number.like(f"{prefix}%"))
            .order_by(RFQ.rfq_number.desc())
            .limit(1)
        )
        return await self.session.scalar(stmt)

    async def list_all(self) -> list[RFQ]:
        stmt = select(RFQ).where(RFQ.deleted_at.is_(None)).order_by(RFQ.created_at.desc())
        return list((await self.session.execute(stmt)).scalars().all())