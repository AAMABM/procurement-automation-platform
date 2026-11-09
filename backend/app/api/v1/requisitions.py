"""
Purchase Requisition API endpoints.
"""
from uuid import UUID
from fastapi import APIRouter, Depends, status

from app.api.deps import CurrentUser, PRSvc, require_permissions
from app.core.permissions import PermissionCode
from app.schemas.requisition import PRCreate, PRResponse

router = APIRouter(prefix="/requisitions", tags=["Purchase Requisitions"])

@router.get(
    "",
    response_model=list[PRResponse],
    dependencies=[Depends(require_permissions(PermissionCode.REQUISITIONS_READ.value))],
)
async def list_requisitions(prs: PRSvc) -> list[PRResponse]:
    prs_list = await prs.list()
    return [PRResponse.model_validate(p) for p in prs_list]

@router.post(
    "",
    response_model=PRResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permissions(PermissionCode.REQUISITIONS_WRITE.value))],
)
async def create_requisition(
    payload: PRCreate, 
    prs: PRSvc, 
    current_user: CurrentUser
) -> PRResponse:
    """Creates a PR in DRAFT status."""
    pr = await prs.create_draft(payload, current_user)
    return PRResponse.model_validate(pr)

@router.post(
    "/{pr_id}/submit",
    response_model=PRResponse,
    dependencies=[Depends(require_permissions(PermissionCode.REQUISITIONS_WRITE.value))],
)
async def submit_requisition(
    pr_id: UUID, 
    prs: PRSvc, 
    current_user: CurrentUser
) -> PRResponse:
    """Submits a DRAFT PR, generating the official PR number."""
    pr = await prs.submit(pr_id, current_user)
    return PRResponse.model_validate(pr)

@router.post(
    "/{pr_id}/approve",
    response_model=PRResponse,
    dependencies=[Depends(require_permissions(PermissionCode.REQUISITIONS_APPROVE.value))],
)
async def approve_requisition(pr_id: UUID, prs: PRSvc) -> PRResponse:
    """Approves a SUBMITTED PR."""
    pr = await prs.approve(pr_id)
    return PRResponse.model_validate(pr)

@router.post(
    "/{pr_id}/reject",
    response_model=PRResponse,
    dependencies=[Depends(require_permissions(PermissionCode.REQUISITIONS_APPROVE.value))],
)
async def reject_requisition(pr_id: UUID, prs: PRSvc) -> PRResponse:
    """Rejects a SUBMITTED PR."""
    pr = await prs.reject(pr_id)
    return PRResponse.model_validate(pr)