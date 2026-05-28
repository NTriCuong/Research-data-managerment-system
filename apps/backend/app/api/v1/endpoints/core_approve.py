from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import require_roles
from app.database.session import get_db
from app.models.auth.user import User
from app.schemas.auth import MessageResponse
from app.schemas.core_approve import ApproveRequest, CoreSearchResultOut, PendingApprovalOut, RejectApprovalRequest
from app.services.staging.core_approve_service import core_approve_service

router = APIRouter()

ALLOWED_APPROVER_ROLES = ("SUPER_ADMIN", "APPROVER")
ALLOWED_SEARCH_ROLES = ("SUPER_ADMIN", "APPROVER", "REVIEWER", "DATA_ENTRY")


async def _commit_if_supported(db: AsyncSession) -> None:
    commit = getattr(db, "commit", None)
    if callable(commit):
        await commit()


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
        note=payload.note,
        current_user=current_user,
    )
    await _commit_if_supported(db)
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
    await _commit_if_supported(db)
    return result


@router.get("/search", response_model=list[CoreSearchResultOut])
async def search_core_postgres(
    q: str = Query(min_length=1, max_length=300),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    _: User = Depends(require_roles(*ALLOWED_SEARCH_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> list[CoreSearchResultOut]:
    return await core_approve_service.search_core_postgres(db, query=q.strip(), limit=limit, offset=offset)
