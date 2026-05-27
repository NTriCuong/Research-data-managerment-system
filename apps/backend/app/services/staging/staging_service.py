from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth.user import User
from app.models.enum import WorkflowStatus
from app.models.staging.stg_file_attachment import StgFileAttachment
from app.models.staging.stg_research_object import StgResearchObject
from app.models.staging.stg_research_object_author import StgResearchObjectAuthor
from app.models.staging.stg_research_object_domain import StgResearchObjectDomain
from app.models.staging.stg_research_object_keyword import StgResearchObjectKeyword
from app.repositories.staging_repository import StagingRepository
from app.schemas.auth import MessageResponse
from app.schemas.staging_metadata import (
    CreateRevisionRequest,
    StagingFileOut,
    StagingResearchObjectCreate,
    StagingResearchObjectOut,
    StagingResearchObjectUpdate,
    SubmitForReviewRequest,
)
from app.services.storage.file_service import file_service
from app.services.logs.workflow_service import workflow_service


class StagingService:
    def _assert_editable(self, staging_obj: StgResearchObject, user: User) -> None:
        if staging_obj.created_by != user.user_id and user.role.role_code != "SUPER_ADMIN":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot edit this staging record")
        if staging_obj.workflow_status not in (WorkflowStatus.draft, WorkflowStatus.revision_required):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only draft or revision_required records can be edited",
            )

    def _validate_before_submit(self, staging_obj: StgResearchObject) -> None:
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

    async def create_staging_research_object(
        self,
        db: AsyncSession,
        *,
        payload: StagingResearchObjectCreate,
        current_user: User,
    ) -> StagingResearchObjectOut:
        repo = StagingRepository(db)
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
        await repo.create(obj)

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
        await workflow_service.write_history(
            db,
            staging_id=obj.staging_id,
            performed_by=current_user.user_id,
            from_status=None,
            to_status=WorkflowStatus.draft,
            action_code="CREATE_DRAFT",
        )
        await db.refresh(obj)
        return StagingResearchObjectOut.model_validate(obj)

    async def list_my_staging_records(
        self,
        db: AsyncSession,
        *,
        current_user: User,
        workflow_status: WorkflowStatus | None,
        limit: int,
        offset: int,
    ) -> list[StagingResearchObjectOut]:
        repo = StagingRepository(db)
        rows = await repo.list_by_creator(
            creator_id=current_user.user_id,
            workflow_status=workflow_status,
            limit=limit,
            offset=offset,
        )
        return [StagingResearchObjectOut.model_validate(x) for x in rows]

    async def get_staging_record(self, db: AsyncSession, *, staging_id: UUID, current_user: User) -> StagingResearchObjectOut:
        repo = StagingRepository(db)
        obj = await repo.get_by_id(staging_id)
        if obj is None or obj.deleted_at is not None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staging record not found")
        if obj.created_by != current_user.user_id and current_user.role.role_code != "SUPER_ADMIN":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot view this staging record")
        return StagingResearchObjectOut.model_validate(obj)

    async def update_staging_record(
        self,
        db: AsyncSession,
        *,
        staging_id: UUID,
        payload: StagingResearchObjectUpdate,
        current_user: User,
    ) -> StagingResearchObjectOut:
        repo = StagingRepository(db)
        obj = await repo.get_by_id(staging_id, with_relations=True)
        if obj is None or obj.deleted_at is not None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staging record not found")
        self._assert_editable(obj, current_user)

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

        await workflow_service.write_history(
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

    async def submit_for_review(
        self,
        db: AsyncSession,
        *,
        staging_id: UUID,
        payload: SubmitForReviewRequest,
        current_user: User,
    ) -> MessageResponse:
        repo = StagingRepository(db)
        obj = await repo.get_by_id(staging_id, with_relations=True)
        if obj is None or obj.deleted_at is not None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staging record not found")
        self._assert_editable(obj, current_user)
        self._validate_before_submit(obj)

        old_status = obj.workflow_status
        obj.workflow_status = WorkflowStatus.pending_review
        obj.submitted_by = current_user.user_id
        obj.submitted_at = datetime.now(timezone.utc)
        await workflow_service.write_history(
            db,
            staging_id=obj.staging_id,
            performed_by=current_user.user_id,
            from_status=old_status,
            to_status=WorkflowStatus.pending_review,
            action_code="SUBMIT_FOR_REVIEW",
            action_note=payload.note,
        )
        return MessageResponse(message="Submitted for review")

    async def create_revision_from_core(
        self,
        db: AsyncSession,
        *,
        payload: CreateRevisionRequest,
        current_user: User,
    ) -> StagingResearchObjectOut:
        repo = StagingRepository(db)
        core_obj = await repo.get_core_by_id_with_relations(payload.research_id)
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
        await repo.create(revision)

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
        await workflow_service.write_history(
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

    async def create_staging_file_metadata(
        self,
        db: AsyncSession,
        *,
        staging_id: UUID,
        file: UploadFile,
        access_level: str,
        current_user: User,
    ) -> StagingFileOut:
        repo = StagingRepository(db)
        obj = await repo.get_by_id(staging_id)
        if obj is None or obj.deleted_at is not None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staging record not found")
        self._assert_editable(obj, current_user)

        uploaded = await file_service.prepare_file_upload(staging_id=staging_id, file=file, access_level=access_level)
        file_obj = StgFileAttachment(
            staging_id=staging_id,
            original_filename=uploaded["original_filename"],
            stored_filename=uploaded["stored_filename"],
            storage_path=uploaded["storage_path"],
            mime_type=uploaded["mime_type"],
            file_extension=uploaded["file_extension"],
            file_size_bytes=uploaded["file_size_bytes"],
            checksum_sha256=uploaded["checksum_sha256"],
            uploaded_by=current_user.user_id,
            access_level=uploaded["access_level"],
        )
        await repo.add_file_attachment(file_obj)
        await workflow_service.write_history(
            db,
            staging_id=staging_id,
            performed_by=current_user.user_id,
            from_status=None,
            to_status=obj.workflow_status,
            action_code="UPLOAD_EVIDENCE_FILE",
            action_note=uploaded["original_filename"],
        )
        await db.refresh(file_obj)
        return StagingFileOut.model_validate(file_obj)


staging_service = StagingService()
