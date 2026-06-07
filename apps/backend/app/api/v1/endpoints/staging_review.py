from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import require_roles
from app.database.session import get_db
from app.models.auth.user import User
from app.schemas.auth import MessageResponse
from app.schemas.staging_metadata import StagingResearchObjectOut
from app.schemas.staging_review import ForwardToApprovalRequest, RequestRevisionRequest
from app.services.staging.staging_review_service import staging_review_service

router = APIRouter()

ALLOWED_REVIEWER_ROLES = ("SUPER_ADMIN", "REVIEWER")


@router.get("/pending", response_model=list[StagingResearchObjectOut])
async def list_pending_review_records(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    _: User = Depends(require_roles(*ALLOWED_REVIEWER_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> list[StagingResearchObjectOut]:
    return await staging_review_service.list_pending_review_records(
        db,
        limit=limit,
        offset=offset,
    )


@router.post("/{staging_id}/request-revision", response_model=MessageResponse)
async def request_revision(
    staging_id: UUID,
    payload: RequestRevisionRequest,
    current_user: User = Depends(require_roles(*ALLOWED_REVIEWER_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    result = await staging_review_service.request_revision(
        db,
        staging_id=staging_id,
        payload=payload,
        current_user=current_user,
    )
    return result


@router.post("/{staging_id}/forward", response_model=MessageResponse)
async def forward_to_approval(
    staging_id: UUID,
    payload: ForwardToApprovalRequest,
    current_user: User = Depends(require_roles(*ALLOWED_REVIEWER_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    result = await staging_review_service.forward_to_approval(
        db,
        staging_id=staging_id,
        payload=payload,
        current_user=current_user,
    )
    return result
