from datetime import datetime, timezone
from uuid import UUID

from app.core.access_levels import is_access_level_allowed
from app.core.exceptions import BadRequestException, NotFoundException
from fastapi import BackgroundTasks
from app.models.auth.user import User
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.core_repository import CoreRepository
from app.schemas.core_repository import (
    CoreAuthorOut,
    CoreFileOut,
    CoreMetadataVersionOut,
    CoreResearchObjectDetailOut,
    CoreResearchObjectListOut,
)
from app.models.enum import AccessLevel, FileStatus
from app.services.logs.audit_service import audit_service
from app.services.search.elasticsearch_index_service import index_research_document


class CoreRepositoryService:
    async def list_core_records(self, db: AsyncSession, *, limit: int, offset: int) -> list[CoreResearchObjectListOut]:
        repo = CoreRepository(db)
        rows = await repo.list_core_records(limit=limit, offset=offset)
        return [CoreResearchObjectListOut.model_validate(row) for row in rows]

    async def list_my_core_records(
        self,
        db: AsyncSession,
        *,
        creator_id: UUID,
        limit: int,
        offset: int,
    ) -> list[CoreResearchObjectListOut]:
        repo = CoreRepository(db)
        rows = await repo.list_core_records_by_creator(
            creator_id=creator_id,
            limit=limit,
            offset=offset,
        )
        return [CoreResearchObjectListOut.model_validate(row) for row in rows]

    async def get_core_record(self, db: AsyncSession, *, research_id: UUID) -> CoreResearchObjectDetailOut:
        repo = CoreRepository(db)
        core_obj = await repo.get_core_record(research_id, with_relations=True)
        if core_obj is None:
            raise NotFoundException("Không tìm thấy bản ghi core")

        return CoreResearchObjectDetailOut(
            **CoreResearchObjectListOut.model_validate(core_obj).model_dump(),
            source_staging_id=core_obj.source_staging_id,
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
            metadata_quality_detail=core_obj.metadata_quality_detail,
            domain_ids=[item.domain_id for item in core_obj.domains],
            keyword_ids=[item.keyword_id for item in core_obj.keywords],
            authors=[CoreAuthorOut.model_validate(item) for item in sorted(core_obj.authors, key=lambda x: x.author_order)],
            file_attachments=[CoreFileOut.model_validate(item) for item in core_obj.file_attachments],
        )

    async def list_core_files(self, db: AsyncSession, *, research_id: UUID) -> list[CoreFileOut]:
        core_obj = await CoreRepository(db).get_core_record(research_id, with_relations=True)
        if core_obj is None:
            raise NotFoundException("Không tìm thấy bản ghi core")
        return [CoreFileOut.model_validate(item) for item in core_obj.file_attachments]

    async def update_core_file_access_level(
        self,
        db: AsyncSession,
        *,
        research_id: UUID,
        file_id: UUID,
        access_level: AccessLevel,
        current_user: User,
    ) -> CoreFileOut:
        core_obj = await CoreRepository(db).get_core_record(research_id, with_relations=True)
        if core_obj is None:
            raise NotFoundException("Không tìm thấy bản ghi core")

        file_obj = next(
            (item for item in core_obj.file_attachments if item.file_id == file_id),
            None,
        )
        if file_obj is None:
            raise NotFoundException("Không tìm thấy tệp của bản ghi core")
        if file_obj.file_status == FileStatus.deleted:
            raise BadRequestException("Không thể cập nhật quyền của tệp đã bị xóa")
        if not is_access_level_allowed(access_level, core_obj.access_level):
            raise BadRequestException(
                "Quyền truy cập của tệp không được cao hơn quyền truy cập của bài nghiên cứu"
            )

        previous_access_level = file_obj.access_level
        if previous_access_level == access_level:
            return CoreFileOut.model_validate(file_obj)

        file_obj.access_level = access_level
        core_obj.updated_at = datetime.now(timezone.utc)
        await audit_service.write_log(
            db,
            actor_user_id=current_user.user_id,
            action_code="UPDATE_CORE_FILE_ACCESS_LEVEL",
            target_schema="core",
            target_table="file_attachments",
            target_id=file_obj.file_id,
            old_value={
                "research_id": str(research_id),
                "access_level": previous_access_level.value,
            },
            new_value={
                "research_id": str(research_id),
                "access_level": access_level.value,
            },
            message="Updated access level for an approved evidence file",
        )
        await db.flush()
        return CoreFileOut.model_validate(file_obj)

    async def update_core_research_access_level(
        self,
        db: AsyncSession,
        *,
        research_id: UUID,
        access_level: AccessLevel,
        background_tasks: BackgroundTasks,
        current_user: User,
    ) -> CoreResearchObjectListOut:
        core_obj = await CoreRepository(db).get_core_record(research_id, with_relations=True)
        if core_obj is None:
            raise NotFoundException("Không tìm thấy bản ghi core")

        previous_access_level = core_obj.access_level
        if previous_access_level == access_level:
            return CoreResearchObjectListOut.model_validate(core_obj)

        lowered_file_ids: list[str] = []
        for file_obj in core_obj.file_attachments:
            if file_obj.file_status == FileStatus.deleted:
                continue
            if is_access_level_allowed(file_obj.access_level, access_level):
                continue

            old_file_access_level = file_obj.access_level
            file_obj.access_level = access_level
            lowered_file_ids.append(str(file_obj.file_id))
            await audit_service.write_log(
                db,
                actor_user_id=current_user.user_id,
                action_code="CASCADE_CORE_FILE_ACCESS_LEVEL",
                target_schema="core",
                target_table="file_attachments",
                target_id=file_obj.file_id,
                old_value={
                    "research_id": str(research_id),
                    "access_level": old_file_access_level.value,
                },
                new_value={
                    "research_id": str(research_id),
                    "access_level": access_level.value,
                },
                message="Lowered file access level to match its approved research",
            )

        core_obj.access_level = access_level
        core_obj.updated_at = datetime.now(timezone.utc)
        await audit_service.write_log(
            db,
            actor_user_id=current_user.user_id,
            action_code="UPDATE_CORE_RESEARCH_ACCESS_LEVEL",
            target_schema="core",
            target_table="research_objects",
            target_id=core_obj.research_id,
            old_value={"access_level": previous_access_level.value},
            new_value={
                "access_level": access_level.value,
                "lowered_file_ids": lowered_file_ids,
            },
            message="Updated access level for an approved research",
        )
        await db.flush()
        await db.commit()
        background_tasks.add_task(
            index_research_document,
            core_obj.research_id,
        )
        return CoreResearchObjectListOut.model_validate(core_obj)

    async def list_metadata_versions(self, db: AsyncSession, *, research_id: UUID) -> list[CoreMetadataVersionOut]:
        core_obj = await CoreRepository(db).get_core_record(research_id, with_relations=True)
        if core_obj is None:
            raise NotFoundException("Không tìm thấy bản ghi core")
        versions = sorted(core_obj.metadata_versions, key=lambda item: item.version_no, reverse=True)
        return [CoreMetadataVersionOut.model_validate(item) for item in versions]


core_repository_service = CoreRepositoryService()
