from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import ConflictError
from app.models.vendor import Vendor
from app.repositories.vendor_repository import VendorRepository
from app.schemas.vendor import VendorCreate

class VendorService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.vendors = VendorRepository(session)

    async def create(self, payload: VendorCreate) -> Vendor:
        if payload.sap_vendor_number:
            existing = await self.vendors.get_by(sap_vendor_number=payload.sap_vendor_number)
            if existing:
                raise ConflictError("A vendor with this SAP number already exists.")
                
        vendor = Vendor(**payload.model_dump())
        await self.vendors.add(vendor)
        await self.session.commit()
        await self.session.refresh(vendor)
        return vendor

    async def list(self) -> list[Vendor]:
        return await self.vendors.list_all()