"""
Vendor API endpoints.
"""
from fastapi import APIRouter, Depends, status

from app.api.deps import VendorSvc, require_permissions
from app.core.permissions import PermissionCode
from app.schemas.vendor import VendorCreate, VendorResponse

router = APIRouter(prefix="/vendors", tags=["Vendors"])

@router.get(
    "",
    response_model=list[VendorResponse],
    dependencies=[Depends(require_permissions(PermissionCode.VENDORS_READ.value))],
)
async def list_vendors(vendors: VendorSvc) -> list[VendorResponse]:
    items = await vendors.list()
    return [VendorResponse.model_validate(v) for v in items]

@router.post(
    "",
    response_model=VendorResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permissions(PermissionCode.VENDORS_WRITE.value))],
)
async def create_vendor(payload: VendorCreate, vendors: VendorSvc) -> VendorResponse:
    vendor = await vendors.create(payload)
    return VendorResponse.model_validate(vendor)