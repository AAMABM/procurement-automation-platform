"""
Purchase Order API endpoints.
"""
from fastapi import APIRouter, Depends, status

from app.api.deps import POSvc, require_permissions
from app.core.permissions import PermissionCode
from app.schemas.purchase_order import POCreate, POResponse

router = APIRouter(prefix="/purchase-orders", tags=["Purchase Orders"])

@router.get(
    "",
    response_model=list[POResponse],
    dependencies=[Depends(require_permissions(PermissionCode.PURCHASE_ORDERS_READ.value))],
)
async def list_purchase_orders(pos: POSvc) -> list[POResponse]:
    items = await pos.list()
    return [POResponse.model_validate(po) for po in items]

@router.post(
    "",
    response_model=POResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permissions(PermissionCode.PURCHASE_ORDERS_WRITE.value))],
)
async def create_purchase_order(payload: POCreate, pos: POSvc) -> POResponse:
    """Converts an APPROVED PR into a PO."""
    po = await pos.create_from_pr(payload)
    return POResponse.model_validate(po)