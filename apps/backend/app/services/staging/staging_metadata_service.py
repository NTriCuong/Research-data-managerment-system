from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth.user import User
from app.models.enum import FileStatus, WorkflowStatus
from app.models.staging.stg_file_attachment import StgFileAttachment
from app.models.staging.stg_research_object import StgResearchObject
from app.models.staging.stg_research_object_author import StgResearchObjectAuthor
from app.models.staging.stg_research_object_domain import StgResearchObjectDomain
from app.models.staging.stg_research_object_keyword import StgResearchObjectKeyword
from app.repositories.staging_metadata_repository import StagingRepository
from app.schemas.auth import MessageResponse
from app.schemas.staging_metadata import (
    BulkSubmitForReviewItemOut,
    BulkSubmitForReviewOut,
    BulkSubmitForReviewRequest,
    CreateRevisionRequest,
    StagingFileOut,
    StagingResearchObjectCreate,
    StagingResearchObjectOut,
    StagingResearchObjectUpdate,
    SubmitForReviewRequest,
    WorkflowHistoryOut,
)
from app.services.logs.audit_service import audit_service
from app.services.storage.file_service import file_service
from app.services.logs.workflow_service import workflow_service
from fastapi.encoders import jsonable_encoder
from pydantic import AnyUrl

class StagingService:
    def _recalculate_metadata_quality(self, staging_obj: StgResearchObject) -> None:
        checks: dict[str, bool] = {
            "title": bool(staging_obj.title and staging_obj.title.strip()),
            "output_type_id": staging_obj.output_type_id is not None,
            "department_id": staging_obj.department_id is not None,
            "year": staging_obj.year is not None and 1900 <= staging_obj.year <= datetime.now(timezone.utc).year,
            "authors": len(staging_obj.authors) > 0,
            "domains": len(staging_obj.domains) > 0,
            "keywords": len(staging_obj.keywords) > 0,
        }
        passed = sum(1 for ok in checks.values() if ok)
        score = (Decimal(passed) * Decimal("100")) / Decimal(len(checks))
        staging_obj.metadata_quality_score = score.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        staging_obj.metadata_quality_detail = {
            "passed": passed,
            "total": len(checks),
            "checks": checks,
        }

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
        has_invalid_author = any(not x.full_name or not x.full_name.strip() for x in staging_obj.authors)
        if has_invalid_author:
            missing.append("authors.full_name")
        if missing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required metadata before submit: {', '.join(missing)}",
            )

    async def _submit_one_for_review(
        self,
        db: AsyncSession,
        *,
        repo: StagingRepository,
        staging_id: UUID,
        note: str | None,
        current_user: User,
        now: datetime | None = None,
    ) -> None:
        obj = await repo.get_by_id(staging_id, with_relations=True)
        if obj is None or obj.deleted_at is not None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staging record not found")
        self._assert_editable(obj, current_user)
        self._validate_before_submit(obj)
        if not await repo.has_active_file_attachment(staging_id=staging_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one file attachment is required before submit",
            )

        old_status = obj.workflow_status
        submitted_at = now or datetime.now(timezone.utc)
        obj.workflow_status = WorkflowStatus.pending_review
        obj.submitted_by = current_user.user_id
        obj.submitted_at = submitted_at
        obj.updated_at = submitted_at
        await workflow_service.write_history(
            db,
            staging_id=obj.staging_id,
            performed_by=current_user.user_id,
            from_status=old_status,
            to_status=WorkflowStatus.pending_review,
            action_code="SUBMIT_FOR_REVIEW",
            action_note=note,
        )
        await audit_service.write_log(
            db,
            actor_user_id=current_user.user_id,
            action_code="SUBMIT_FOR_REVIEW",
            target_schema="staging",
            target_table="research_objects",
            target_id=obj.staging_id,
            old_value={"workflow_status": old_status.value},
            new_value={"workflow_status": WorkflowStatus.pending_review.value, "note": note},
            message="Submitted staging record for review",
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
            external_url=str(payload.external_url) if payload.external_url else None,
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
        await audit_service.write_log(
            db,
            actor_user_id=current_user.user_id,
            action_code="CREATE_DRAFT",
            target_schema="staging",
            target_table="research_objects",
            target_id=obj.staging_id,
            new_value={"workflow_status": WorkflowStatus.draft.value, "title": obj.title},
            message="Created staging draft",
        )
        obj = await repo.get_by_id(obj.staging_id, with_relations=True) or obj
        self._recalculate_metadata_quality(obj)
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

    async def list_all_staging_records(
        self,
        db: AsyncSession,
        *,
        workflow_status: WorkflowStatus | None,
        limit: int,
        offset: int,
    ) -> list[StagingResearchObjectOut]:
        repo = StagingRepository(db)
        rows = await repo.list_all(
            workflow_status=workflow_status,
            limit=limit,
            offset=offset,
        )
        return [StagingResearchObjectOut.model_validate(x) for x in rows]

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
        now = datetime.now(timezone.utc)
        
        payload_data = payload.model_dump(exclude_unset=True)
        
        changed_old: dict = {}
        changed_new: dict = {}
        
        for field, value in payload_data.items():
            if field in {"domain_ids", "keyword_ids", "authors"}:
                continue    
            if isinstance(value, AnyUrl):
                value = str(value)
            old = getattr(obj, field)

            if old != value:
                changed_old[field] = old
                changed_new[field] = value
                setattr(obj, field, value)

        # 2. Update domains
        if payload.domain_ids is not None:
            old_domain_ids = [x.domain_id for x in obj.domains]
            new_domain_ids = payload.domain_ids

            if set(old_domain_ids) != set(new_domain_ids):
                changed_old["domain_ids"] = [str(x) for x in old_domain_ids]
                changed_new["domain_ids"] = [str(x) for x in new_domain_ids]

                obj.domains.clear()
                await db.flush()
                obj.domains.extend(
                    [
                        StgResearchObjectDomain(
                            staging_id=obj.staging_id,
                            domain_id=domain_id,
                        )
                        for domain_id in new_domain_ids
                    ]
                )

        # 3. Update keywords
        if payload.keyword_ids is not None:
            old_keyword_ids = [x.keyword_id for x in obj.keywords]
            new_keyword_ids = payload.keyword_ids

            if set(old_keyword_ids) != set(new_keyword_ids):
                changed_old["keyword_ids"] = [str(x) for x in old_keyword_ids]
                changed_new["keyword_ids"] = [str(x) for x in new_keyword_ids]

                obj.keywords.clear()
                await db.flush()
                obj.keywords.extend(
                    [
                        StgResearchObjectKeyword(
                            staging_id=obj.staging_id,
                            keyword_id=keyword_id,
                        )
                        for keyword_id in new_keyword_ids
                    ]
                )

        # 4. Update authors
        if payload.authors is not None:
            old_authors = [
                {
                    "researcher_id": str(x.researcher_id) if x.researcher_id else None,
                    "full_name": x.full_name,
                    "email": x.email,
                    "affiliation": x.affiliation,
                    "author_order": x.author_order,
                    "author_role": x.author_role.value if hasattr(x.author_role, "value") else x.author_role,
                }
                for x in obj.authors
            ]

            new_authors = [
                {
                    "researcher_id": str(author.researcher_id) if author.researcher_id else None,
                    "full_name": author.full_name,
                    "email": author.email,
                    "affiliation": author.affiliation,
                    "author_order": author.author_order,
                    "author_role": author.author_role.value if hasattr(author.author_role, "value") else author.author_role,
                }
                for author in payload.authors
            ]

            if old_authors != new_authors:
                changed_old["authors"] = old_authors
                changed_new["authors"] = new_authors

                obj.authors.clear()
                await db.flush()
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

        obj.updated_at = now
        self._recalculate_metadata_quality(obj)

        # 5. Chỉ ghi audit nếu thật sự có thay đổi
        if changed_old or changed_new:
            changed_new["updated_at"] = now.isoformat()
            
            await audit_service.write_log(
                db,
                actor_user_id=current_user.user_id,
                action_code="UPDATE_DRAFT",
                target_schema="staging",
                target_table="research_objects",
                target_id=obj.staging_id,
                old_value=jsonable_encoder(changed_old),
                new_value=jsonable_encoder(changed_new),
                message="Updated staging draft metadata",
                created_at=now,
            )
        await db.flush()
        await db.refresh(obj)
        return StagingResearchObjectOut.model_validate(obj)

    async def delete_draft_staging_record(
        self,
        db: AsyncSession,
        *,
        staging_id: UUID,
        current_user: User,
    ) -> MessageResponse:
        repo = StagingRepository(db)
        obj = await repo.get_by_id(staging_id)
        if obj is None or obj.deleted_at is not None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staging record not found")
        if obj.created_by != current_user.user_id and current_user.role.role_code != "SUPER_ADMIN":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot delete this staging record")
        if obj.workflow_status != WorkflowStatus.draft:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only draft records can be deleted")

        now = datetime.now(timezone.utc)
        obj.deleted_at = now
        obj.updated_at = now
        await audit_service.write_log(
            db,
            actor_user_id=current_user.user_id,
            action_code="DELETE_DRAFT",
            target_schema="staging",
            target_table="research_objects",
            target_id=obj.staging_id,
            message="Soft deleted staging draft",
        )
        return MessageResponse(message="Draft deleted")

    async def submit_for_review(
        self,
        db: AsyncSession,
        *,
        staging_id: UUID,
        payload: SubmitForReviewRequest,
        current_user: User,
    ) -> MessageResponse:
        repo = StagingRepository(db)
        await self._submit_one_for_review(
            db,
            repo=repo,
            staging_id=staging_id,
            note=payload.note,
            current_user=current_user,
        )
        return MessageResponse(message="Submitted for review")

    async def bulk_submit_for_review(
        self,
        db: AsyncSession,
        *,
        payload: BulkSubmitForReviewRequest,
        current_user: User,
    ) -> BulkSubmitForReviewOut:
        repo = StagingRepository(db)
        now = datetime.now(timezone.utc)
        results: list[BulkSubmitForReviewItemOut] = []
        seen: set[UUID] = set()

        for staging_id in payload.staging_ids:
            if staging_id in seen:
                results.append(
                    BulkSubmitForReviewItemOut(
                        staging_id=staging_id,
                        success=False,
                        message="Duplicate staging_id in request",
                    )
                )
                continue
            seen.add(staging_id)

            try:
                await self._submit_one_for_review(
                    db,
                    repo=repo,
                    staging_id=staging_id,
                    note=payload.note,
                    current_user=current_user,
                    now=now,
                )
            except HTTPException as exc:
                results.append(
                    BulkSubmitForReviewItemOut(
                        staging_id=staging_id,
                        success=False,
                        message=str(exc.detail),
                    )
                )
                continue

            results.append(
                BulkSubmitForReviewItemOut(
                    staging_id=staging_id,
                    success=True,
                    message="Submitted for review",
                )
            )

        submitted_count = sum(1 for x in results if x.success)
        return BulkSubmitForReviewOut(
            submitted_count=submitted_count,
            failed_count=len(results) - submitted_count,
            results=results,
        )

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
            external_url=str(core_obj.external_url) if core_obj.external_url else None,
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
        await audit_service.write_log(
            db,
            actor_user_id=current_user.user_id,
            action_code="CREATE_REVISION_DRAFT",
            target_schema="staging",
            target_table="research_objects",
            target_id=revision.staging_id,
            new_value={"workflow_status": WorkflowStatus.draft.value, "update_reason": payload.update_reason},
            message="Created revision draft from core research object",
        )
        revision = await repo.get_by_id(revision.staging_id, with_relations=True) or revision
        self._recalculate_metadata_quality(revision)
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
        obj = await repo.get_by_id(staging_id, with_relations=True)
        if obj is None or obj.deleted_at is not None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staging record not found")
        self._assert_editable(obj, current_user)
        obj.updated_at = datetime.now(timezone.utc)

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
        await audit_service.write_log(
            db,
            actor_user_id=current_user.user_id,
            action_code="UPLOAD_EVIDENCE_FILE",
            target_schema="staging",
            target_table="research_objects",
            target_id=obj.staging_id,
            new_value={"filename": uploaded["original_filename"], "workflow_status": obj.workflow_status.value},
            message="Uploaded staging evidence file metadata",
        )
        self._recalculate_metadata_quality(obj)
        await db.refresh(file_obj)
        return StagingFileOut.model_validate(file_obj)

    async def list_staging_files(
        self,
        db: AsyncSession,
        *,
        staging_id: UUID,
        current_user: User,
    ) -> list[StagingFileOut]:
        repo = StagingRepository(db)
        obj = await repo.get_by_id(staging_id)
        if obj is None or obj.deleted_at is not None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staging record not found")
        if obj.created_by != current_user.user_id and current_user.role.role_code not in {"SUPER_ADMIN", "MANAGER"}:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot view files of this staging record")
        files = await repo.list_file_attachments(staging_id=staging_id)
        return [StagingFileOut.model_validate(x) for x in files]

    async def list_all_staging_files(
        self,
        db: AsyncSession,
        *,
        include_deleted: bool,
        limit: int,
        offset: int,
    ) -> list[StagingFileOut]:
        repo = StagingRepository(db)
        files = await repo.list_all_file_attachments(
            include_deleted=include_deleted,
            limit=limit,
            offset=offset,
        )
        return [StagingFileOut.model_validate(x) for x in files]

    async def delete_staging_file(
        self,
        db: AsyncSession,
        *,
        staging_id: UUID,
        file_id: UUID,
        current_user: User,
    ) -> MessageResponse:
        repo = StagingRepository(db)
        obj = await repo.get_by_id(staging_id)
        if obj is None or obj.deleted_at is not None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staging record not found")
        self._assert_editable(obj, current_user)
        file_obj = await repo.get_file_attachment(staging_id=staging_id, file_id=file_id)
        if file_obj is None or file_obj.file_status == FileStatus.deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staging file not found")

        previous_file_status = file_obj.file_status
        file_obj.file_status = FileStatus.deleted
        obj.updated_at = datetime.now(timezone.utc)
        await audit_service.write_log(
            db,
            actor_user_id=current_user.user_id,
            action_code="DELETE_EVIDENCE_FILE",
            target_schema="staging",
            target_table="file_attachments",
            target_id=file_obj.file_id,
            old_value={"file_status": previous_file_status.value},
            new_value={"file_status": FileStatus.deleted.value},
            message="Soft deleted staging evidence file",
        )
        return MessageResponse(message="File deleted")

    async def list_staging_workflow_history(
        self,
        db: AsyncSession,
        *,
        staging_id: UUID,
        current_user: User,
        limit: int,
        offset: int,
    ) -> list[WorkflowHistoryOut]:
        repo = StagingRepository(db)
        obj = await repo.get_by_id(staging_id)
        if obj is None or obj.deleted_at is not None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staging record not found")
        if obj.created_by != current_user.user_id and current_user.role.role_code not in {"SUPER_ADMIN", "MANAGER"}:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot view this staging workflow history")
        rows = await repo.list_workflow_history(staging_id=staging_id, limit=limit, offset=offset)
        return [WorkflowHistoryOut.model_validate(x) for x in rows]


staging_service = StagingService()
