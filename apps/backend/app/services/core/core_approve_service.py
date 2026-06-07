from datetime import datetime, timezone
from uuid import UUID

from app.core.exceptions import BadRequestException, NotFoundException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth.user import User
from app.models.core.core_file_attachment import CoreFileAttachment
from app.models.core.core_metadata_version import CoreMetadataVersion
from app.models.core.core_research_object import CoreResearchObject
from app.models.core.core_research_object_author import CoreResearchObjectAuthor
from app.models.core.core_research_object_domain import CoreResearchObjectDomain
from app.models.core.core_research_object_keyword import CoreResearchObjectKeyword
from app.models.enum import AccessLevel, WorkflowStatus
from app.repositories.core_approve_repository import CoreApproveRepository
from app.schemas.auth import MessageResponse
from app.schemas.core_approve import ApproveRequest, PendingApprovalOut
from app.services.logs.audit_service import audit_service
from app.services.logs.workflow_service import workflow_service


class CoreApproveService:
    _REFRESH_SEARCH_VECTOR_SQL = text(
        """
        UPDATE core.research_objects AS ro
        SET search_vector =
            setweight(to_tsvector('simple', unaccent(coalesce(ro.title, ''))), 'A') ||
            setweight(to_tsvector('simple', unaccent(coalesce(ro.identifier, ''))), 'A') ||
            setweight(to_tsvector('simple', unaccent(coalesce(ro.abstract, ''))), 'B') ||
            setweight(to_tsvector('simple', unaccent(coalesce((
                SELECT string_agg(
                    concat_ws(' ', a.full_name, a.email, a.affiliation),
                    ' '
                    ORDER BY a.author_order
                )
                FROM core.research_object_authors AS a
                WHERE a.research_id = ro.research_id
            ), ''))), 'B') ||
            setweight(to_tsvector('simple', unaccent(coalesce((
                SELECT string_agg(concat_ws(' ', k.keyword_text, k.normalized_text), ' ' ORDER BY k.keyword_text)
                FROM core.research_object_keywords AS rok
                JOIN reference.keywords AS k ON k.keyword_id = rok.keyword_id
                WHERE rok.research_id = ro.research_id
            ), ''))), 'B') ||
            setweight(to_tsvector('simple', unaccent(coalesce((
                SELECT string_agg(concat_ws(' ', d.domain_code, d.domain_name, d.description), ' ' ORDER BY d.domain_name)
                FROM core.research_object_domains AS rod
                JOIN reference.research_domains AS d ON d.domain_id = rod.domain_id
                WHERE rod.research_id = ro.research_id
            ), ''))), 'B') ||
            setweight(to_tsvector('simple', unaccent(coalesce(ro.description, ''))), 'C')
        WHERE ro.research_id = CAST(:research_id AS uuid)
        """
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

    async def list_pending_approval_records(self, db: AsyncSession, *, limit: int, offset: int) -> list[PendingApprovalOut]:
        repo = CoreApproveRepository(db)
        rows = await repo.list_pending_approval_records(limit=limit, offset=offset)
        return [PendingApprovalOut.model_validate(x) for x in rows]

    async def approve_record(
        self,
        db: AsyncSession,
        *,
        staging_id: UUID,
        payload: ApproveRequest,
        current_user: User,
    ) -> MessageResponse:
        access_level = payload.access_level
        file_access_levels = {item.file_id: item.access_level for item in payload.file_access_levels}
        repo = CoreApproveRepository(db)
        staging_obj = await repo.get_staging_by_id(staging_id, with_relations=True)
        if staging_obj is None or staging_obj.deleted_at is not None:
            raise NotFoundException("Không tìm thấy bản ghi tạm")

        self._assert_pending_approval(staging_obj.workflow_status)
        unknown_file_ids = set(file_access_levels) - {file_obj.file_id for file_obj in staging_obj.file_attachments}
        if unknown_file_ids:
            raise BadRequestException("Một hoặc nhiều file_access_levels tham chiếu đến tệp không thuộc bản ghi tạm này")

        now = datetime.now(timezone.utc)
        previous_status = staging_obj.workflow_status

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
            self._copy_staging_into_core(staging_obj, core_obj, now, current_user.user_id)
            db.add(core_obj)
            await db.flush()
        else:
            core_obj = await repo.get_core_by_id(staging_obj.source_core_research_id, with_relations=True)
            if core_obj is None or core_obj.deleted_at is not None:
                raise NotFoundException("Không tìm thấy bản ghi core nguồn")

            old_snapshot = self._build_snapshot(core_obj)
            core_obj.version_no += 1
            self._copy_staging_into_core(staging_obj, core_obj, now, current_user.user_id)
            db.add(
                CoreMetadataVersion(
                    research_id=core_obj.research_id,
                    version_no=core_obj.version_no,
                    metadata_snapshot=old_snapshot,
                    change_reason=staging_obj.update_reason,
                    created_by=current_user.user_id,
                    created_at=now,
                )
            )

            core_obj.authors.clear()
            core_obj.domains.clear()
            core_obj.keywords.clear()
            core_obj.file_attachments.clear()
            await db.flush()

        core_obj.access_level = access_level
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
        core_obj.domains.extend(
            [CoreResearchObjectDomain(research_id=core_obj.research_id, domain_id=d.domain_id) for d in staging_obj.domains]
        )
        core_obj.keywords.extend(
            [CoreResearchObjectKeyword(research_id=core_obj.research_id, keyword_id=k.keyword_id) for k in staging_obj.keywords]
        )
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
                    access_level=file_access_levels.get(f.file_id, access_level),
                )
                for f in staging_obj.file_attachments
            ]
        )

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
            old_value={"workflow_status": previous_status.value},
            new_value={
                "workflow_status": WorkflowStatus.approved.value,
                "research_id": str(core_obj.research_id),
                "access_level": access_level.value,
            },
            message="Approver approved staging record and published to core",
        )
        await db.flush()
        await self._refresh_search_vector(db, research_id=core_obj.research_id)
        return MessageResponse(message="Phê duyệt và xuất bản bản ghi vào core thành công")

    async def reject_record(self, db: AsyncSession, *, staging_id: UUID, reason: str, current_user: User) -> MessageResponse:
        repo = CoreApproveRepository(db)
        staging_obj = await repo.get_staging_by_id(staging_id)
        if staging_obj is None or staging_obj.deleted_at is not None:
            raise NotFoundException("Không tìm thấy bản ghi tạm")

        self._assert_pending_approval(staging_obj.workflow_status)
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
            old_value={"workflow_status": previous_status.value},
            new_value={"workflow_status": WorkflowStatus.rejected.value, "rejection_reason": reason},
            message="Approver rejected staging record",
        )
        return MessageResponse(message="Từ chối bản ghi thành công")

    async def _refresh_search_vector(self, db: AsyncSession, *, research_id: UUID) -> None:
        await db.execute(self._REFRESH_SEARCH_VECTOR_SQL, {"research_id": str(research_id)})

core_approve_service = CoreApproveService()
