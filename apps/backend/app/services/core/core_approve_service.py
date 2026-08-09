from datetime import datetime, timezone
from email import message
from uuid import UUID

from app.core.exceptions import BadRequestException, NotFoundException
from app.core.access_levels import is_access_level_allowed
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import BackgroundTasks
from app.database.session import AsyncSessionLocal

from app.models.auth.user import User
from app.models.core.core_file_attachment import CoreFileAttachment
from app.models.core.core_metadata_version import CoreMetadataVersion
from app.models.core.core_research_object import CoreResearchObject
from app.models.core.core_research_object_author import CoreResearchObjectAuthor
from app.models.core.core_research_object_domain import CoreResearchObjectDomain
from app.models.core.core_research_object_keyword import CoreResearchObjectKeyword
from app.models.enum import AccessLevel, FileStatus, NotificationType, WorkflowStatus
from app.repositories.core_approve_repository import CoreApproveRepository
from app.schemas.auth import MessageResponse
from app.schemas.core_approve import ApproveRequest, PendingApprovalOut
from app.services.logs.audit_service import audit_service
from app.services.logs.workflow_service import workflow_service
from app.core.config import settings
from app.services.notification.notification_service import notification_service, push_to_users
from app.services.search.elasticsearch_index_service import index_research_document


class CoreApproveService:
    _REFRESH_SEARCH_VECTOR_SQL = text(
        "SELECT app.refresh_core_search_vector(CAST(:research_id AS uuid))"
    )

    @staticmethod
    def _assert_pending_approval(status_value: WorkflowStatus) -> None:
        if status_value != WorkflowStatus.pending_approval:
            raise BadRequestException("Chỉ bản ghi ở trạng thái pending_approval mới có thể được phê duyệt hoặc từ chối")

    @staticmethod
    def _copy_staging_into_core(staging_obj, core_obj: CoreResearchObject, now: datetime, approver_user_id: UUID) -> None:
        fields = [
            "title",
            "description",
            "abstract",
            "output_type_id",
            "department_id",
            "year",
            "start_date",
            "end_date",
            "date_issued",
            "publisher",
            "language",
            "identifier",
            "external_url",
            "source",
            "relation",
            "coverage",
            "rights",
            "metadata_quality_score",
            "metadata_quality_detail",
        ]
        for field in fields:
            setattr(core_obj, field, getattr(staging_obj, field))

        core_obj.source_staging_id = staging_obj.staging_id
        core_obj.approved_by = approver_user_id
        core_obj.approved_at = now
        core_obj.updated_at = now

    @staticmethod
    def _build_snapshot(core_obj: CoreResearchObject) -> dict:
        return {
            "research_id": str(core_obj.research_id),
            "title": core_obj.title,
            "description": core_obj.description,
            "abstract": core_obj.abstract,
            "output_type_id": str(core_obj.output_type_id),
            "department_id": str(core_obj.department_id),
            "year": core_obj.year,
            "start_date": core_obj.start_date.isoformat() if core_obj.start_date else None,
            "end_date": core_obj.end_date.isoformat() if core_obj.end_date else None,
            "date_issued": core_obj.date_issued.isoformat() if core_obj.date_issued else None,
            "publisher": core_obj.publisher,
            "language": core_obj.language,
            "identifier": core_obj.identifier,
            "external_url": core_obj.external_url,
            "source": core_obj.source,
            "relation": core_obj.relation,
            "coverage": core_obj.coverage,
            "rights": core_obj.rights,
            "access_level": core_obj.access_level.value,
            "version_no": core_obj.version_no,
            "authors": [
                {
                    "researcher_id": str(x.researcher_id) if x.researcher_id else None,
                    "full_name": x.full_name,
                    "email": x.email,
                    "affiliation": x.affiliation,
                    "author_order": x.author_order,
                    "author_role": x.author_role.value,
                }
                for x in core_obj.authors
            ],
            "domain_ids": [str(x.domain_id) for x in core_obj.domains],
            "keyword_ids": [str(x.keyword_id) for x in core_obj.keywords],
        }

    @staticmethod
    def _metadata_version_for(
        *,
        core_obj: CoreResearchObject,
        staging_obj,
        current_user: User,
        created_at: datetime,
        note: str | None,
    ) -> CoreMetadataVersion:
        return CoreMetadataVersion(
            research_id=core_obj.research_id,
            version_no=core_obj.version_no,
            metadata_snapshot=CoreApproveService._build_snapshot(core_obj),
            change_reason=staging_obj.update_reason or note,
            created_by=current_user.user_id,
            created_at=created_at,
        )

    async def list_pending_approval_records(self, db: AsyncSession, *, limit: int, offset: int) -> list[PendingApprovalOut]:
        repo = CoreApproveRepository(db)
        rows = await repo.list_pending_approval_records(limit=limit, offset=offset)
        return [PendingApprovalOut.model_validate(x) for x in rows]

    async def _refresh_search_vector(self, db: AsyncSession, *, research_id: UUID) -> None:
            await db.execute(self._REFRESH_SEARCH_VECTOR_SQL, {"research_id": str(research_id)})

    async def approve_record(
        self,
        db: AsyncSession,
        *,
        staging_id: UUID,
        payload: ApproveRequest,
        background_tasks: BackgroundTasks,
        current_user: User,
    ) -> MessageResponse:
        try:
            repo = CoreApproveRepository(db)

            staging_obj = await repo.get_staging_by_id(
                staging_id,
                with_relations=True,
            )

            if staging_obj is None or staging_obj.deleted_at is not None:
                raise NotFoundException("Không tìm thấy bản ghi tạm")


            self._assert_pending_approval(
                staging_obj.workflow_status
            )


            access_level = staging_obj.access_level


            for file_obj in staging_obj.file_attachments:
                if file_obj.file_status == FileStatus.deleted:
                    continue
                if not is_access_level_allowed(
                    file_obj.access_level,
                    access_level,
                ):
                    raise BadRequestException(
                        f"Quyền truy cập của tệp "
                        f"'{file_obj.original_filename}' "
                        "không được cao hơn quyền truy cập "
                        "của bài nghiên cứu"
                    )


            now = datetime.now(timezone.utc)

            previous_status = staging_obj.workflow_status

            # CREATE / UPDATE CORE RESEARCH

            if staging_obj.source_core_research_id is None:

                core_obj = CoreResearchObject(
                    source_staging_id=staging_obj.staging_id,
                    approved_by=current_user.user_id,
                    approved_at=now,
                    access_level=access_level,
                    version_no=1,
                    is_current=True,
                    authors=[],
                    domains=[],
                    keywords=[],
                    file_attachments=[],
                )

                self._copy_staging_into_core(
                    staging_obj,
                    core_obj,
                    now,
                    current_user.user_id,
                )

                db.add(core_obj)

                await db.flush()


            else:

                core_obj = await repo.get_core_by_id(
                    staging_obj.source_core_research_id,
                    with_relations=True,
                )

                if core_obj is None or core_obj.deleted_at is not None:
                    raise NotFoundException(
                        "Không tìm thấy bản ghi core nguồn"
                    )


                core_obj.version_no += 1


                self._copy_staging_into_core(
                    staging_obj,
                    core_obj,
                    now,
                    current_user.user_id,
                )


                core_obj.authors.clear()
                core_obj.domains.clear()
                core_obj.keywords.clear()
                core_obj.file_attachments.clear()


                await db.flush()

            core_obj.access_level = access_level

            # authors

            core_obj.authors.extend(
                [
                    CoreResearchObjectAuthor(
                        research_id=core_obj.research_id,
                        researcher_id=a.researcher_id,
                        full_name=a.full_name,
                        email=a.email,
                        affiliation=a.affiliation,
                        author_order=a.author_order,
                        author_role=a.author_role,
                    )
                    for a in staging_obj.authors
                ]
            )


            # domains

            core_obj.domains.extend(
                [
                    CoreResearchObjectDomain(
                        research_id=core_obj.research_id,
                        domain_id=d.domain_id,
                    )
                    for d in staging_obj.domains
                ]
            )


            # keywords

            core_obj.keywords.extend(
                [
                    CoreResearchObjectKeyword(
                        research_id=core_obj.research_id,
                        keyword_id=k.keyword_id,
                    )
                    for k in staging_obj.keywords
                ]
            )


            # files

            core_obj.file_attachments.extend(
                [
                    CoreFileAttachment(
                        research_id=core_obj.research_id,
                        original_filename=f.original_filename,
                        stored_filename=f.stored_filename,
                        storage_path=f.storage_path,
                        mime_type=f.mime_type,
                        file_extension=f.file_extension,
                        file_size_bytes=f.file_size_bytes,
                        checksum_sha256=f.checksum_sha256,
                        uploaded_by=f.uploaded_by,
                        uploaded_at=f.uploaded_at,
                        access_level=f.access_level,
                    )
                    for f in staging_obj.file_attachments
                    if f.file_status != FileStatus.deleted
                ]
            )


            # metadata version

            db.add(
                self._metadata_version_for(
                    core_obj=core_obj,
                    staging_obj=staging_obj,
                    current_user=current_user,
                    created_at=now,
                    note=payload.note,
                )
            )


            # UPDATE WORKFLOW STATUS

            staging_obj.workflow_status = WorkflowStatus.approved
            staging_obj.approved_by = current_user.user_id
            staging_obj.approved_at = now
            staging_obj.updated_at = now



            await workflow_service.write_history(
                db,
                staging_id=staging_obj.staging_id,
                research_id=core_obj.research_id,
                performed_by=current_user.user_id,
                from_status=previous_status,
                to_status=WorkflowStatus.approved,
                action_code="APPROVE_RECORD",
                action_note=payload.note,
            )


            await audit_service.write_log(
                db,
                actor_user_id=current_user.user_id,
                action_code="APPROVE_RECORD",
                target_schema="staging",
                target_table="research_objects",
                target_id=staging_obj.staging_id,
                old_value={
                    "workflow_status": previous_status.value,
                },
                new_value={
                    "workflow_status": WorkflowStatus.approved.value,
                    "research_id": str(core_obj.research_id),
                    "access_level": access_level.value,
                },
                message=(
                    "Approver approved staging record "
                    "and published to core"
                ),
            )


            await db.flush()


            await self._refresh_search_vector(
                db,
                research_id=core_obj.research_id,
            )


            await db.commit()


            background_tasks.add_task(
                index_research_document,
                core_obj.research_id,
            )



            title = "Bài nghiên cứu đã được phê duyệt"

            message = (
                f"Bài nghiên cứu '{staging_obj.title}' "
                "đã được phê duyệt và xuất bản vào core."
            )


            background_tasks.add_task(
                self.notify_approval_background,
                recipient_user_id=staging_obj.created_by,
                actor_user_id=current_user.user_id,
                staging_id=staging_obj.staging_id,
                research_id=core_obj.research_id,
                title=title,
                message=message,
            )


            return MessageResponse(
                message="Phê duyệt và xuất bản bản ghi vào core thành công"
            )

        except Exception:
            await db.rollback()
            raise


    async def notify_approval_background(
        self,
        *,
        recipient_user_id: UUID,
        actor_user_id: UUID,
        staging_id: UUID,
        research_id: UUID,
        title: str,
        message: str,
    ) -> None:

        async with AsyncSessionLocal() as db:

            try:

                await notification_service.notify_user(
                    db,
                    recipient_user_id=recipient_user_id,
                    actor_user_id=actor_user_id,
                    event_type=NotificationType.APPROVAL.value,
                    title=title,
                    message=message,
                    target_url=(
                        f"{settings.FRONTEND_URL}"
                        f"/dashboard/data-entry/researches/{staging_id}"
                    ),
                    payload={
                        "staging_id": str(staging_id),
                        "research_id": str(research_id),
                        "workflow_status": (
                            WorkflowStatus.approved.value
                        ),
                    },
                )

                await db.commit()


                await push_to_users(
                    db,
                    [recipient_user_id],
                    title,
                    message,
                )
            except Exception:
                await db.rollback()


    async def reject_record(
        self,
        db: AsyncSession,
        *,
        staging_id: UUID,
        reason: str,
        background_tasks: BackgroundTasks,
        current_user: User,
    ) -> MessageResponse:

        try:
            repo = CoreApproveRepository(db)

            staging_obj = await repo.get_staging_by_id(staging_id)

            if staging_obj is None or staging_obj.deleted_at is not None:
                raise NotFoundException(
                    "Không tìm thấy bản ghi tạm"
                )


            self._assert_pending_approval(
                staging_obj.workflow_status
            )


            if not reason.strip():
                raise BadRequestException(
                    "Lý do từ chối không được để trống"
                )


            now = datetime.now(timezone.utc)

            previous_status = staging_obj.workflow_status


            staging_obj.workflow_status = WorkflowStatus.rejected
            staging_obj.rejection_reason = reason
            staging_obj.approved_by = current_user.user_id
            staging_obj.approved_at = now
            staging_obj.updated_at = now



            await workflow_service.write_history(
                db,
                staging_id=staging_obj.staging_id,
                performed_by=current_user.user_id,
                from_status=previous_status,
                to_status=WorkflowStatus.rejected,
                action_code="REJECT_RECORD",
                action_note=reason,
            )



            await audit_service.write_log(
                db,
                actor_user_id=current_user.user_id,
                action_code="REJECT_RECORD",
                target_schema="staging",
                target_table="research_objects",
                target_id=staging_obj.staging_id,
                old_value={
                    "workflow_status": previous_status.value,
                },
                new_value={
                    "workflow_status": WorkflowStatus.rejected.value,
                    "rejection_reason": reason,
                },
                message="Approver rejected staging record",
            )


            await db.commit()



            title = "Bài nghiên cứu bị từ chối"

            message = (
                f"Bài nghiên cứu '{staging_obj.title}' "
                f"bị từ chối: {reason}"
            )


            background_tasks.add_task(
                self.notify_rejection_background,
                recipient_user_id=staging_obj.created_by,
                actor_user_id=current_user.user_id,
                staging_id=staging_obj.staging_id,
                title=title,
                message=message,
                reason=reason,
            )


            return MessageResponse(
                message="Từ chối bản ghi thành công"
            )


        except Exception:
            await db.rollback()
            raise   


    async def notify_rejection_background(
        self,
        *,
        recipient_user_id: UUID,
        actor_user_id: UUID,
        staging_id: UUID,
        title: str,
        message: str,
        reason: str,
    ) -> None:

        async with AsyncSessionLocal() as db:

            try:

                await notification_service.notify_user(
                    db,
                    recipient_user_id=recipient_user_id,
                    actor_user_id=actor_user_id,
                    event_type=NotificationType.REJECTED.value,
                    title=title,
                    message=message,
                    target_url=(
                        f"{settings.FRONTEND_URL}"
                        f"/dashboard/data-entry/researches/{staging_id}"
                    ),
                    payload={
                        "staging_id": str(staging_id),
                        "workflow_status": (
                            WorkflowStatus.rejected.value
                        ),
                        "reason": reason,
                    },
                )


                await db.commit()


                await push_to_users(
                    db,
                    [recipient_user_id],
                    title,
                    message,
                )


            except Exception:

                await db.rollback()

core_approve_service = CoreApproveService()
