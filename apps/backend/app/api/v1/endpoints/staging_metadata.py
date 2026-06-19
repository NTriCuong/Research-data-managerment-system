from uuid import UUID

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import require_roles
from app.database.session import get_db
from app.models.auth.user import User
from app.models.enum import WorkflowStatus
from app.schemas.auth import MessageResponse
from app.schemas.files import IncomingFile
from app.schemas.staging_metadata import (
    BulkSubmitForReviewOut,
    BulkSubmitForReviewRequest,
    CreateRevisionRequest,
    StagingFileOut,
    StagingResearchObjectCreate,
    StagingResearchObjectDetailOut,
    StagingResearchObjectOut,
    StagingResearchObjectUpdate,
    SubmitForReviewRequest,
    WorkflowHistoryOut,
)
from app.services.staging.staging_metadata_service import staging_service

router = APIRouter()

ALLOWED_EDITOR_ROLES = ("SUPER_ADMIN", "DATA_ENTRY")
ALLOWED_ADMIN_MANAGER_ROLES = ("SUPER_ADMIN", "MANAGER")
ALLOWED_STAGING_VIEWER_ROLES = ("SUPER_ADMIN", "MANAGER", "DATA_ENTRY", "REVIEWER", "APPROVER")


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


@router.get("", response_model=list[StagingResearchObjectOut])
async def list_all_staging_records(
    workflow_status: WorkflowStatus | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    _: User = Depends(require_roles(*ALLOWED_ADMIN_MANAGER_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> list[StagingResearchObjectOut]:
    return await staging_service.list_all_staging_records(
        db,
        workflow_status=workflow_status,
        limit=limit,
        offset=offset,
    )


@router.get("/files", response_model=list[StagingFileOut])
async def list_all_staging_file_metadata(
    include_deleted: bool = Query(default=False),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    _: User = Depends(require_roles("SUPER_ADMIN")),
    db: AsyncSession = Depends(get_db),
) -> list[StagingFileOut]:
    return await staging_service.list_all_staging_files(
        db,
        include_deleted=include_deleted,
        limit=limit,
        offset=offset,
    )


@router.post("/submit-bulk", response_model=BulkSubmitForReviewOut)
async def bulk_submit_for_review(
    payload: BulkSubmitForReviewRequest,
    current_user: User = Depends(require_roles(*ALLOWED_EDITOR_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> BulkSubmitForReviewOut:
    result = await staging_service.bulk_submit_for_review(
        db,
        payload=payload,
        current_user=current_user,
    )
    return result


@router.get("/{staging_id}", response_model=StagingResearchObjectDetailOut)
async def get_staging_record(
    staging_id: UUID,
    current_user: User = Depends(require_roles(*ALLOWED_STAGING_VIEWER_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> StagingResearchObjectDetailOut:
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
    return result


@router.delete("/{staging_id}", response_model=MessageResponse)
async def delete_draft_staging_record(
    staging_id: UUID,
    current_user: User = Depends(require_roles(*ALLOWED_EDITOR_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    result = await staging_service.delete_draft_staging_record(
        db,
        staging_id=staging_id,
        current_user=current_user,
    )
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
    return result


@router.get("/{staging_id}/workflow-history", response_model=list[WorkflowHistoryOut])
async def list_staging_workflow_history(
    staging_id: UUID,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(require_roles(*ALLOWED_STAGING_VIEWER_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> list[WorkflowHistoryOut]:
    return await staging_service.list_staging_workflow_history(
        db,
        staging_id=staging_id,
        current_user=current_user,
        limit=limit,
        offset=offset,
    )


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
    return result


@router.get("/{staging_id}/files", response_model=list[StagingFileOut])
async def list_staging_file_metadata(
    staging_id: UUID,
    current_user: User = Depends(require_roles(*ALLOWED_STAGING_VIEWER_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> list[StagingFileOut]:
    return await staging_service.list_staging_files(
        db,
        staging_id=staging_id,
        current_user=current_user,
    )


@router.post("/{staging_id}/files", response_model=StagingFileOut, status_code=status.HTTP_201_CREATED)
async def create_staging_file_metadata(
    staging_id: UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(require_roles(*ALLOWED_EDITOR_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> StagingFileOut:
    incoming_file = IncomingFile(
        filename=file.filename or "uploaded-file",
        content_type=file.content_type or "application/octet-stream",
        fileobj=file.file,
    )
    result = await staging_service.create_staging_file_metadata(
        db,
        staging_id=staging_id,
        file=incoming_file,
        current_user=current_user,
    )
    return result


@router.delete("/{staging_id}/files/{file_id}", response_model=MessageResponse)
async def delete_staging_file_metadata(
    staging_id: UUID,
    file_id: UUID,
    current_user: User = Depends(require_roles(*ALLOWED_EDITOR_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    result = await staging_service.delete_staging_file(
        db,
        staging_id=staging_id,
        file_id=file_id,
        current_user=current_user,
)
    return result
