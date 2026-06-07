from uuid import UUID

from app.core.exceptions import NotFoundException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.core_repository import CoreRepository
from app.schemas.core_repository import (
    CoreAuthorOut,
    CoreFileOut,
    CoreMetadataVersionOut,
    CoreResearchObjectDetailOut,
    CoreResearchObjectListOut,
)


class CoreRepositoryService:
    async def list_core_records(self, db: AsyncSession, *, limit: int, offset: int) -> list[CoreResearchObjectListOut]:
        repo = CoreRepository(db)
        rows = await repo.list_core_records(limit=limit, offset=offset)
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

    async def list_metadata_versions(self, db: AsyncSession, *, research_id: UUID) -> list[CoreMetadataVersionOut]:
        core_obj = await CoreRepository(db).get_core_record(research_id, with_relations=True)
        if core_obj is None:
            raise NotFoundException("Không tìm thấy bản ghi core")
        versions = sorted(core_obj.metadata_versions, key=lambda item: item.version_no, reverse=True)
        return [CoreMetadataVersionOut.model_validate(item) for item in versions]


core_repository_service = CoreRepositoryService()
