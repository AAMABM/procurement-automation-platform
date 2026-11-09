from sqlalchemy import select
from app.models.vendor import Vendor
from app.repositories.base import BaseRepository

class VendorRepository(BaseRepository[Vendor]):
    model = Vendor

    async def list_all(self) -> list[Vendor]:
        stmt = select(Vendor).where(Vendor.deleted_at.is_(None)).order_by(Vendor.name)
        return list((await self.session.execute(stmt)).scalars().all())