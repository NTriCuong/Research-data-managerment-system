from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import require_roles
from app.database.session import get_db
from app.models.auth.user import User
from app.schemas.auth import MessageResponse
from app.schemas.core_approve import ApproveRequest, PendingApprovalOut, RejectApprovalRequest
from app.services.core.core_approve_service import core_approve_service

router = APIRouter()

ALLOWED_APPROVER_ROLES = ("SUPER_ADMIN", "APPROVER")


@router.get("/pending", response_model=list[PendingApprovalOut])
async def list_pending_approval_records(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    _: User = Depends(require_roles(*ALLOWED_APPROVER_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> list[PendingApprovalOut]:
    return await core_approve_service.list_pending_approval_records(db, limit=limit, offset=offset)


@router.post("/{staging_id}/approve", response_model=MessageResponse)
async def approve_record(
    staging_id: UUID,
    payload: ApproveRequest,
    current_user: User = Depends(require_roles(*ALLOWED_APPROVER_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    result = await core_approve_service.approve_record(
        db,
        staging_id=staging_id,
        payload=payload,
        current_user=current_user,
    )
    return result


@router.post("/{staging_id}/reject", response_model=MessageResponse)
async def reject_record(
    staging_id: UUID,
    payload: RejectApprovalRequest,
    current_user: User = Depends(require_roles(*ALLOWED_APPROVER_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    result = await core_approve_service.reject_record(
        db,
        staging_id=staging_id,
        reason=payload.reason,
        current_user=current_user,
    )
    return result
