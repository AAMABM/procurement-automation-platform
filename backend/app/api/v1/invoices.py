from fastapi import APIRouter, Depends, status
from app.api.deps import DB, require_permissions
from app.core.permissions import PermissionCode
from app.schemas.invoice import GRCreate, GRResponse, InvoiceCreate, InvoiceResponse
from app.services.invoice_service import InvoiceService

router = APIRouter(tags=["Invoices & Receipts"])

def get_inv_service(session: DB) -> InvoiceService:
    return InvoiceService(session)

@router.post("/goods-receipts", response_model=GRResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permissions(PermissionCode.PURCHASE_ORDERS_WRITE.value))])
async def create_goods_receipt(payload: GRCreate, svc: InvoiceService = Depends(get_inv_service)) -> GRResponse:
    gr = await svc.create_gr(payload)
    return GRResponse.model_validate(gr)

@router.post("/invoices", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permissions(PermissionCode.INVOICES_WRITE.value))])
async def create_invoice(payload: InvoiceCreate, svc: InvoiceService = Depends(get_inv_service)) -> InvoiceResponse:
    inv = await svc.create_invoice(payload)
    return InvoiceResponse.model_validate(inv)

@router.get("/invoices", response_model=list[InvoiceResponse], dependencies=[Depends(require_permissions(PermissionCode.INVOICES_READ.value))])
async def list_invoices(svc: InvoiceService = Depends(get_inv_service)) -> list[InvoiceResponse]:
    invs = await svc.list()
    return [InvoiceResponse.model_validate(i) for i in invs]