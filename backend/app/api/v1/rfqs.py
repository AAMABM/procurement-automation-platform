from uuid import UUID
from fastapi import APIRouter, Depends, status
from app.api.deps import DB, require_permissions
from app.core.permissions import PermissionCode
from app.schemas.rfq import RFQCreate, RFQResponse, QuotationCreate, QuotationResponse, AwardQuotation
from app.schemas.purchase_order import POResponse
from app.services.rfq_service import RFQService

router = APIRouter(prefix="/rfqs", tags=["RFQs & Sourcing"])

def get_rfq_service(session: DB) -> RFQService:
    return RFQService(session)

@router.get("", response_model=list[RFQResponse], dependencies=[Depends(require_permissions(PermissionCode.REQUISITIONS_READ.value))])
async def list_rfqs(svc: RFQService = Depends(get_rfq_service)) -> list[RFQResponse]:
    return [RFQResponse.model_validate(r) for r in await svc.list()]

@router.post("", response_model=RFQResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permissions(PermissionCode.REQUISITIONS_WRITE.value))])
async def create_rfq(payload: RFQCreate, svc: RFQService = Depends(get_rfq_service)) -> RFQResponse:
    rfq = await svc.create(payload)
    return RFQResponse.model_validate(rfq)

@router.post("/{rfq_id}/quotations", response_model=QuotationResponse, status_code=status.HTTP_201_CREATED)
async def submit_quotation(rfq_id: UUID, payload: QuotationCreate, svc: RFQService = Depends(get_rfq_service)) -> QuotationResponse:
    q = await svc.submit_quotation(rfq_id, payload)
    return QuotationResponse.model_validate(q)

@router.post("/{rfq_id}/award", response_model=POResponse, dependencies=[Depends(require_permissions(PermissionCode.PURCHASE_ORDERS_WRITE.value))])
async def award_quote(rfq_id: UUID, payload: AwardQuotation, svc: RFQService = Depends(get_rfq_service)) -> POResponse:
    po = await svc.award_quotation(rfq_id, payload.quotation_id)
    return POResponse.model_validate(po)