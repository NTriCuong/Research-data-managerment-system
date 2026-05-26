from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import require_roles
from app.database.config import get_db
from app.models.auth.user import User
from app.models.enum import WorkflowStatus
from app.schemas.auth import MessageResponse
from app.schemas.staging_metadata import (
    CreateRevisionRequest,
    StagingFileOut,
    StagingResearchObjectCreate,
    StagingResearchObjectOut,
    StagingResearchObjectUpdate,
    SubmitForReviewRequest,
)
from app.services.staging.staging_service import staging_service

router = APIRouter()

ALLOWED_EDITOR_ROLES = ("SUPER_ADMIN", "DATA_ENTRY")


async def _commit_if_supported(db: AsyncSession) -> None:
    commit = getattr(db, "commit", None)
    if callable(commit):
        await commit()


@router.post("", response_model=StagingResearchObjectOut, status_code=status.HTTP_201_CREATED)
async def create_staging_research_object(
    payload: StagingResearchObjectCreate,
    current_user: User = Depends(require_roles(*ALLOWED_EDITOR_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> StagingResearchObjectOut:
    result = await staging_service.create_staging_research_object(
        db,
        payload=payload,
        current_user=current_user,
    )
    await _commit_if_supported(db)
    return result


@router.get("/mine", response_model=list[StagingResearchObjectOut])
async def list_my_staging_records(
    workflow_status: WorkflowStatus | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(require_roles(*ALLOWED_EDITOR_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> list[StagingResearchObjectOut]:
    return await staging_service.list_my_staging_records(
        db,
        current_user=current_user,
        workflow_status=workflow_status,
        limit=limit,
        offset=offset,
    )


@router.get("/{staging_id}", response_model=StagingResearchObjectOut)
async def get_staging_record(
    staging_id: UUID,
    current_user: User = Depends(require_roles(*ALLOWED_EDITOR_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> StagingResearchObjectOut:
    return await staging_service.get_staging_record(
        db,
        staging_id=staging_id,
        current_user=current_user,
    )


@router.put("/{staging_id}", response_model=StagingResearchObjectOut)
async def update_staging_record(
    staging_id: UUID,
    payload: StagingResearchObjectUpdate,
    current_user: User = Depends(require_roles(*ALLOWED_EDITOR_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> StagingResearchObjectOut:
    result = await staging_service.update_staging_record(
        db,
        staging_id=staging_id,
        payload=payload,
        current_user=current_user,
    )
    await _commit_if_supported(db)
    return result


@router.post("/{staging_id}/submit", response_model=MessageResponse)
async def submit_for_review(
    staging_id: UUID,
    payload: SubmitForReviewRequest,
    current_user: User = Depends(require_roles(*ALLOWED_EDITOR_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    result = await staging_service.submit_for_review(
        db,
        staging_id=staging_id,
        payload=payload,
        current_user=current_user,
    )
    await _commit_if_supported(db)
    return result


@router.post("/revisions", response_model=StagingResearchObjectOut, status_code=status.HTTP_201_CREATED)
async def create_revision_from_core(
    payload: CreateRevisionRequest,
    current_user: User = Depends(require_roles(*ALLOWED_EDITOR_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> StagingResearchObjectOut:
    result = await staging_service.create_revision_from_core(
        db,
        payload=payload,
        current_user=current_user,
    )
    await _commit_if_supported(db)
    return result


@router.post("/{staging_id}/files", response_model=StagingFileOut, status_code=status.HTTP_201_CREATED)
async def create_staging_file_metadata(
    staging_id: UUID,
    file: UploadFile = File(...),
    access_level: str = Form("internal"),
    current_user: User = Depends(require_roles(*ALLOWED_EDITOR_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> StagingFileOut:
    result = await staging_service.create_staging_file_metadata(
        db,
        staging_id=staging_id,
        file=file,
        access_level=access_level,
        current_user=current_user,
    )
    await _commit_if_supported(db)
    return result
