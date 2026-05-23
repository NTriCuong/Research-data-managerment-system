import asyncio
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.permissions import require_roles
from app.database.config import get_db
from app.models.auth.user import User
from app.models.core.core_research_object import CoreResearchObject
from app.models.enum import AccessLevel, WorkflowStatus
from app.models.logs.workflow_history import WorkflowHistory
from app.models.stagging.stg_file_attachment import StgFileAttachment
from app.models.stagging.stg_research_object import StgResearchObject
from app.models.stagging.stg_research_object_author import StgResearchObjectAuthor
from app.models.stagging.stg_research_object_domain import StgResearchObjectDomain
from app.models.stagging.stg_research_object_keyword import StgResearchObjectKeyword
from app.schemas.auth import MessageResponse
from app.schemas.staging_metadata import (
    CreateRevisionRequest,
    StagingFileOut,
    StagingResearchObjectCreate,
    StagingResearchObjectOut,
    StagingResearchObjectUpdate,
    SubmitForReviewRequest,
)
from app.services.r2_storage import upload_bytes_to_r2

router = APIRouter()

ALLOWED_EDITOR_ROLES = ("SUPER_ADMIN", "DATA_ENTRY")


def _assert_editable(staging_obj: StgResearchObject, user: User) -> None:
    if staging_obj.created_by != user.user_id and user.role.role_code != "SUPER_ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot edit this staging record")
    if staging_obj.workflow_status not in (WorkflowStatus.draft, WorkflowStatus.revision_required):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only draft or revision_required records can be edited",
        )


def _validate_before_submit(staging_obj: StgResearchObject) -> None:
    missing: list[str] = []
    if not staging_obj.title:
        missing.append("title")
    if not staging_obj.output_type_id:
        missing.append("output_type_id")
    if not staging_obj.department_id:
        missing.append("department_id")
    if staging_obj.year is None:
        missing.append("year")
    if not staging_obj.domains:
        missing.append("domains")
    if not staging_obj.keywords:
        missing.append("keywords")
    if not staging_obj.authors:
        missing.append("authors")
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing required metadata before submit: {', '.join(missing)}",
        )


async def _write_workflow_history(
    db: AsyncSession,
    *,
    staging_id: UUID,
    research_id: UUID | None = None,
    performed_by: UUID,
    from_status: WorkflowStatus | None,
    to_status: WorkflowStatus,
    action_code: str,
    action_note: str | None = None,
) -> None:
    db.add(
        WorkflowHistory(
            staging_id=staging_id,
            research_id=research_id,
            from_status=from_status,
            to_status=to_status,
            action_code=action_code,
            action_note=action_note,
            performed_by=performed_by,
        )
    )
    await db.flush()


@router.post("", response_model=StagingResearchObjectOut, status_code=status.HTTP_201_CREATED)
async def create_staging_research_object(
    payload: StagingResearchObjectCreate,
    current_user: User = Depends(require_roles(*ALLOWED_EDITOR_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> StagingResearchObjectOut:
    obj = StgResearchObject(
        title=payload.title,
        output_type_id=payload.output_type_id,
        department_id=payload.department_id,
        year=payload.year,
        description=payload.description,
        abstract=payload.abstract,
        start_date=payload.start_date,
        end_date=payload.end_date,
        date_issued=payload.date_issued,
        publisher=payload.publisher,
        language=payload.language,
        identifier=payload.identifier,
        external_url=payload.external_url,
        source=payload.source,
        relation=payload.relation,
        coverage=payload.coverage,
        rights=payload.rights,
        access_level=payload.access_level,
        created_by=current_user.user_id,
    )
    db.add(obj)
    await db.flush()

    db.add_all([StgResearchObjectDomain(staging_id=obj.staging_id, domain_id=domain_id) for domain_id in payload.domain_ids])
    db.add_all([StgResearchObjectKeyword(staging_id=obj.staging_id, keyword_id=keyword_id) for keyword_id in payload.keyword_ids])
    db.add_all(
        [
            StgResearchObjectAuthor(
                staging_id=obj.staging_id,
                researcher_id=author.researcher_id,
                full_name=author.full_name,
                email=author.email,
                affiliation=author.affiliation,
                author_order=author.author_order,
                author_role=author.author_role,
            )
            for author in payload.authors
        ]
    )
    await _write_workflow_history(
        db,
        staging_id=obj.staging_id,
        performed_by=current_user.user_id,
        from_status=None,
        to_status=WorkflowStatus.draft,
        action_code="CREATE_DRAFT",
    )
    await db.refresh(obj)
    return StagingResearchObjectOut.model_validate(obj)


@router.get("/mine", response_model=list[StagingResearchObjectOut])
async def list_my_staging_records(
    workflow_status: WorkflowStatus | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(require_roles(*ALLOWED_EDITOR_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> list[StagingResearchObjectOut]:
    stmt = (
        select(StgResearchObject)
        .where(StgResearchObject.created_by == current_user.user_id)
        .where(StgResearchObject.deleted_at.is_(None))
        .order_by(StgResearchObject.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    if workflow_status is not None:
        stmt = stmt.where(StgResearchObject.workflow_status == workflow_status)
    result = await db.execute(stmt)
    return [StagingResearchObjectOut.model_validate(x) for x in result.scalars().all()]


@router.get("/{staging_id}", response_model=StagingResearchObjectOut)
async def get_staging_record(
    staging_id: UUID,
    current_user: User = Depends(require_roles(*ALLOWED_EDITOR_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> StagingResearchObjectOut:
    result = await db.execute(
        select(StgResearchObject)
        .where(StgResearchObject.staging_id == staging_id)
        .where(StgResearchObject.deleted_at.is_(None))
    )
    obj = result.scalar_one_or_none()
    if obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staging record not found")
    if obj.created_by != current_user.user_id and current_user.role.role_code != "SUPER_ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot view this staging record")
    return StagingResearchObjectOut.model_validate(obj)


@router.put("/{staging_id}", response_model=StagingResearchObjectOut)
async def update_staging_record(
    staging_id: UUID,
    payload: StagingResearchObjectUpdate,
    current_user: User = Depends(require_roles(*ALLOWED_EDITOR_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> StagingResearchObjectOut:
    result = await db.execute(
        select(StgResearchObject)
        .options(
            selectinload(StgResearchObject.domains),
            selectinload(StgResearchObject.keywords),
            selectinload(StgResearchObject.authors),
        )
        .where(StgResearchObject.staging_id == staging_id)
        .where(StgResearchObject.deleted_at.is_(None))
    )
    obj = result.scalar_one_or_none()
    if obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staging record not found")
    _assert_editable(obj, current_user)

    for field, value in payload.model_dump(exclude_unset=True).items():
        if field in {"domain_ids", "keyword_ids", "authors"}:
            continue
        setattr(obj, field, value)

    if payload.domain_ids is not None:
        obj.domains.clear()
        obj.domains.extend([StgResearchObjectDomain(staging_id=obj.staging_id, domain_id=domain_id) for domain_id in payload.domain_ids])
    if payload.keyword_ids is not None:
        obj.keywords.clear()
        obj.keywords.extend([StgResearchObjectKeyword(staging_id=obj.staging_id, keyword_id=keyword_id) for keyword_id in payload.keyword_ids])
    if payload.authors is not None:
        obj.authors.clear()
        obj.authors.extend(
            [
                StgResearchObjectAuthor(
                    staging_id=obj.staging_id,
                    researcher_id=author.researcher_id,
                    full_name=author.full_name,
                    email=author.email,
                    affiliation=author.affiliation,
                    author_order=author.author_order,
                    author_role=author.author_role,
                )
                for author in payload.authors
            ]
        )

    await _write_workflow_history(
        db,
        staging_id=obj.staging_id,
        performed_by=current_user.user_id,
        from_status=None,
        to_status=obj.workflow_status,
        action_code="UPDATE_DRAFT",
    )
    await db.flush()
    await db.refresh(obj)
    return StagingResearchObjectOut.model_validate(obj)


@router.post("/{staging_id}/submit", response_model=MessageResponse)
async def submit_for_review(
    staging_id: UUID,
    payload: SubmitForReviewRequest,
    current_user: User = Depends(require_roles(*ALLOWED_EDITOR_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    result = await db.execute(
        select(StgResearchObject)
        .options(
            selectinload(StgResearchObject.domains),
            selectinload(StgResearchObject.keywords),
            selectinload(StgResearchObject.authors),
        )
        .where(StgResearchObject.staging_id == staging_id)
        .where(StgResearchObject.deleted_at.is_(None))
    )
    obj = result.scalar_one_or_none()
    if obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staging record not found")
    _assert_editable(obj, current_user)
    _validate_before_submit(obj)

    old_status = obj.workflow_status
    obj.workflow_status = WorkflowStatus.pending_review
    obj.submitted_by = current_user.user_id
    obj.submitted_at = datetime.now(timezone.utc)
    await _write_workflow_history(
        db,
        staging_id=obj.staging_id,
        performed_by=current_user.user_id,
        from_status=old_status,
        to_status=WorkflowStatus.pending_review,
        action_code="SUBMIT_FOR_REVIEW",
        action_note=payload.note,
    )
    return MessageResponse(message="Submitted for review")


@router.post("/revisions", response_model=StagingResearchObjectOut, status_code=status.HTTP_201_CREATED)
async def create_revision_from_core(
    payload: CreateRevisionRequest,
    current_user: User = Depends(require_roles(*ALLOWED_EDITOR_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> StagingResearchObjectOut:
    result = await db.execute(
        select(CoreResearchObject)
        .options(
            selectinload(CoreResearchObject.domains),
            selectinload(CoreResearchObject.keywords),
            selectinload(CoreResearchObject.authors),
        )
        .where(CoreResearchObject.research_id == payload.research_id)
        .where(CoreResearchObject.deleted_at.is_(None))
    )
    core_obj = result.scalar_one_or_none()
    if core_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Core research object not found")

    revision = StgResearchObject(
        title=core_obj.title,
        output_type_id=core_obj.output_type_id,
        department_id=core_obj.department_id,
        year=core_obj.year,
        description=core_obj.description,
        abstract=core_obj.abstract,
        start_date=core_obj.start_date,
        end_date=core_obj.end_date,
        date_issued=core_obj.date_issued,
        publisher=core_obj.publisher,
        language=core_obj.language,
        identifier=core_obj.identifier,
        external_url=core_obj.external_url,
        source=core_obj.source,
        relation=core_obj.relation,
        coverage=core_obj.coverage,
        rights=core_obj.rights,
        access_level=core_obj.access_level,
        source_core_research_id=core_obj.research_id,
        update_reason=payload.update_reason,
        created_by=current_user.user_id,
        workflow_status=WorkflowStatus.draft,
    )
    db.add(revision)
    await db.flush()

    db.add_all([StgResearchObjectDomain(staging_id=revision.staging_id, domain_id=x.domain_id) for x in core_obj.domains])
    db.add_all([StgResearchObjectKeyword(staging_id=revision.staging_id, keyword_id=x.keyword_id) for x in core_obj.keywords])
    db.add_all(
        [
            StgResearchObjectAuthor(
                staging_id=revision.staging_id,
                researcher_id=x.researcher_id,
                full_name=x.full_name,
                email=x.email,
                affiliation=x.affiliation,
                author_order=x.author_order,
                author_role=x.author_role,
            )
            for x in core_obj.authors
        ]
    )
    await _write_workflow_history(
        db,
        staging_id=revision.staging_id,
        research_id=core_obj.research_id,
        performed_by=current_user.user_id,
        from_status=None,
        to_status=WorkflowStatus.draft,
        action_code="CREATE_REVISION_DRAFT",
        action_note=payload.update_reason,
    )
    await db.refresh(revision)
    return StagingResearchObjectOut.model_validate(revision)


@router.post("/{staging_id}/files", response_model=StagingFileOut, status_code=status.HTTP_201_CREATED)
async def create_staging_file_metadata(
    staging_id: UUID,
    file: UploadFile = File(...),
    access_level: str = Form("internal"),
    current_user: User = Depends(require_roles(*ALLOWED_EDITOR_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> StagingFileOut:
    result = await db.execute(select(StgResearchObject).where(StgResearchObject.staging_id == staging_id))
    obj = result.scalar_one_or_none()
    if obj is None or obj.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staging record not found")
    _assert_editable(obj, current_user)

    file_bytes = await file.read()
    file_size_bytes = len(file_bytes)
    if file_size_bytes > 50 * 1024 * 1024:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File size exceeds 50MB limit")
    if file_size_bytes == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File cannot be empty")

    original_filename = file.filename or "uploaded-file"
    file_extension = Path(original_filename).suffix.lower() or None
    stored_filename = f"{uuid4().hex}{file_extension or ''}"
    storage_key = f"staging/{staging_id}/{stored_filename}"
    mime_type = file.content_type or "application/octet-stream"
    checksum_sha256 = hashlib.sha256(file_bytes).hexdigest()

    try:
        access_level_enum = AccessLevel(access_level)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid access_level") from exc

    try:
        upload_result = await asyncio.to_thread(
            upload_bytes_to_r2,
            object_key=storage_key,
            data=file_bytes,
            content_type=mime_type,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Failed to upload file to cloud storage") from exc

    file_obj = StgFileAttachment(
        staging_id=staging_id,
        original_filename=original_filename,
        stored_filename=stored_filename,
        storage_path=upload_result.storage_path,
        mime_type=mime_type,
        file_extension=file_extension,
        file_size_bytes=file_size_bytes,
        checksum_sha256=checksum_sha256,
        uploaded_by=current_user.user_id,
        access_level=access_level_enum,
    )
    db.add(file_obj)
    await db.flush()
    await _write_workflow_history(
        db,
        staging_id=staging_id,
        performed_by=current_user.user_id,
        from_status=None,
        to_status=obj.workflow_status,
        action_code="UPLOAD_EVIDENCE_FILE",
        action_note=original_filename,
    )
    await db.refresh(file_obj)
    return StagingFileOut.model_validate(file_obj)
