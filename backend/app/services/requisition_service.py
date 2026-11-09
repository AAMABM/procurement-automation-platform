"""
Purchase Requisition Service.

Implements a strict State Machine:
    DRAFT -> SUBMITTED -> APPROVED / REJECTED / CANCELLED
"""
from datetime import datetime, UTC
from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ValidationError, AuthorizationError
from app.models.requisition import PurchaseRequisition, PRLineItem
from app.models.user import User
from app.repositories.requisition_repository import PRRepository
from app.schemas.requisition import PRCreate


class PRService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.prs = PRRepository(session)

    async def list(self) -> list[PurchaseRequisition]:
        return await self.prs.list_all()

    async def create_draft(self, payload: PRCreate, requester: User) -> PurchaseRequisition:
        """Creates a PR in DRAFT status. Calculates totals securely server-side."""
        # Generate a temporary DRAFT number (UUID based) until submitted
        draft_num = f"DRAFT-{UUID(bytes=bytes(16))}"[:15]
        
        total_amount = Decimal("0.00")
        line_items = []
        
        for item in payload.line_items:
            line_total = item.quantity * item.unit_price
            total_amount += line_total
            line_items.append(
                PRLineItem(
                    **item.model_dump(),
                    total_price=line_total
                )
            )

        pr = PurchaseRequisition(
            pr_number=draft_num,
            title=payload.title,
            requester_id=requester.id,
            status="DRAFT",
            total_amount=total_amount,
            currency=payload.currency,
            justification=payload.justification,
            required_by=payload.required_by,
            line_items=line_items,
        )
        
        await self.prs.add(pr)
        await self.session.commit()
        await self.session.refresh(pr)
        return pr

    async def submit(self, pr_id: UUID, user: User) -> PurchaseRequisition:
        """Locks the PR, generates the official PR number, and sends for approval."""
        pr = await self.prs.get(pr_id)
        if not pr:
            raise ValidationError("PR not found.")
        if pr.requester_id != user.id:
            raise AuthorizationError("You can only submit your own requisitions.")
        if pr.status != "DRAFT":
            raise ValidationError("Only DRAFT requisitions can be submitted.")

        # Generate Official Number (e.g., PR-2026-00001)
        current_year = datetime.now(UTC).year
        latest_pr = await self.prs.get_latest_pr_number_for_year(current_year)
        
        if latest_pr:
            seq = int(latest_pr.split("-")[-1]) + 1
        else:
            seq = 1
            
        pr.pr_number = f"PR-{current_year}-{seq:05d}"
        pr.status = "SUBMITTED"
        
        await self.session.commit()
        await self.session.refresh(pr)
        return pr

    async def approve(self, pr_id: UUID) -> PurchaseRequisition:
        pr = await self.prs.get(pr_id)
        if not pr:
            raise ValidationError("PR not found.")
        if pr.status != "SUBMITTED":
            raise ValidationError("Only SUBMITTED requisitions can be approved.")
            
        pr.status = "APPROVED"
        await self.session.commit()
        await self.session.refresh(pr)
        return pr

    async def reject(self, pr_id: UUID) -> PurchaseRequisition:
        pr = await self.prs.get(pr_id)
        if not pr:
            raise ValidationError("PR not found.")
        if pr.status != "SUBMITTED":
            raise ValidationError("Only SUBMITTED requisitions can be rejected.")
            
        pr.status = "REJECTED"
        await self.session.commit()
        await self.session.refresh(pr)
        return pr