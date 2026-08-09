import logging
from uuid import UUID

from sqlalchemy import exists, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import BadRequestException, NotFoundException
from app.core.config import settings
from app.models.core.core_file_attachment import CoreFileAttachment
from app.models.core.core_research_object import CoreResearchObject
from app.models.core.core_research_object_author import CoreResearchObjectAuthor
from app.models.core.core_research_object_domain import CoreResearchObjectDomain
from app.models.core.core_research_object_keyword import CoreResearchObjectKeyword
from app.models.enum import AccessLevel, FileStatus
from app.models.reference.department import Department
from app.models.reference.keyword import Keyword
from app.models.reference.output_type import OutputType
from app.models.reference.research_domain import ResearchDomain
from app.models.reference.researcher import Researcher
from app.schemas.public_research import (
    PublicAuthorOut,
    PublicFacetLookupOut,
    PublicFileOut,
    PublicLookupOut,
    PublicResearchDetailOut,
    PublicResearchDownloadOut,
    PublicResearchLookupsOut,
    PublicResearchListItemOut,
    PublicResearchListOut,
    PublicResearchSuggestionOut,
)
from app.services.search.elasticsearch_search_service import (
    ElasticsearchSearchError,
    elasticsearch_search_service,
)
from app.services.storage.r2_storage import create_presigned_download_url


DOWNLOAD_URL_TTL_SECONDS = 300
logger = logging.getLogger(__name__)


class PublicResearchService:
    @staticmethod
    def _base_options():
        return (
            selectinload(CoreResearchObject.output_type),
            selectinload(CoreResearchObject.department),
            selectinload(CoreResearchObject.authors),
            selectinload(CoreResearchObject.domains).selectinload(CoreResearchObjectDomain.domain),
            selectinload(CoreResearchObject.keywords).selectinload(CoreResearchObjectKeyword.keyword),
            selectinload(CoreResearchObject.file_attachments),
        )

    @staticmethod
    def _filters(
        *,
        q: str | None,
        output_type_ids: list[UUID] | None,
        department_ids: list[UUID] | None,
        domain_ids: list[UUID] | None,
        keyword_ids: list[UUID] | None,
        author_ids: list[UUID] | None,
        year_from: int | None,
        year_to: int | None,
        has_files: bool,
    ):
        filters = [
            CoreResearchObject.deleted_at.is_(None),
            CoreResearchObject.is_current.is_(True),
            CoreResearchObject.access_level == AccessLevel.public,
        ]
        if q:
            pattern = func.unaccent(f"%{q.strip()}%")
            filters.append(
                or_(
                    func.unaccent(func.coalesce(CoreResearchObject.title, "")).ilike(pattern),
                    func.unaccent(func.coalesce(CoreResearchObject.description, "")).ilike(pattern),
                    func.unaccent(func.coalesce(CoreResearchObject.abstract, "")).ilike(pattern),
                    func.unaccent(func.coalesce(CoreResearchObject.identifier, "")).ilike(pattern),
                    exists()
                    .where(CoreResearchObjectAuthor.research_id == CoreResearchObject.research_id)
                    .where(func.unaccent(CoreResearchObjectAuthor.full_name).ilike(pattern)),
                )
            )
        if output_type_ids:
            filters.append(CoreResearchObject.output_type_id.in_(output_type_ids))
        if department_ids:
            filters.append(CoreResearchObject.department_id.in_(department_ids))
        if domain_ids:
            filters.append(
                exists()
                .where(CoreResearchObjectDomain.research_id == CoreResearchObject.research_id)
                .where(CoreResearchObjectDomain.domain_id.in_(domain_ids))
            )
        if keyword_ids:
            filters.append(
                exists()
                .where(CoreResearchObjectKeyword.research_id == CoreResearchObject.research_id)
                .where(CoreResearchObjectKeyword.keyword_id.in_(keyword_ids))
            )
        if author_ids:
            filters.append(
                exists()
                .where(CoreResearchObjectAuthor.research_id == CoreResearchObject.research_id)
                .where(CoreResearchObjectAuthor.researcher_id.in_(author_ids))
            )
        if year_from is not None:
            filters.append(CoreResearchObject.year >= year_from)
        if year_to is not None:
            filters.append(CoreResearchObject.year <= year_to)
        if has_files:
            filters.append(
                exists()
                .where(CoreFileAttachment.research_id == CoreResearchObject.research_id)
                .where(CoreFileAttachment.file_status == FileStatus.active)
                .where(CoreFileAttachment.access_level == AccessLevel.public)
            )
        return filters

    @staticmethod
    def _to_lookup(id_value: UUID, name: str) -> PublicLookupOut:
        return PublicLookupOut(id=id_value, name=name)

    @staticmethod
    def _to_facet_lookup(id_value: UUID, name: str, count: int) -> PublicFacetLookupOut:
        return PublicFacetLookupOut(id=id_value, name=name, count=count)

    @staticmethod
    def _cover_image_url(research_id: UUID) -> str | None:
        if not settings.CLOUDFLARE_R2_PUBLIC_BASE_URL:
            return None
        base_url = settings.CLOUDFLARE_R2_PUBLIC_BASE_URL.rstrip("/")
        return f"{base_url}/public/research-covers/{research_id}.jpg"

    async def get_public_lookups(self, db: AsyncSession) -> PublicResearchLookupsOut:
        public_filters = (
            CoreResearchObject.deleted_at.is_(None),
            CoreResearchObject.is_current.is_(True),
            CoreResearchObject.access_level == AccessLevel.public,
        )
        output_types = (
            await db.execute(
                select(OutputType.output_type_id, OutputType.type_name, func.count(CoreResearchObject.research_id))
                .join(CoreResearchObject, CoreResearchObject.output_type_id == OutputType.output_type_id)
                .where(OutputType.is_active.is_(True), *public_filters)
                .group_by(OutputType.output_type_id, OutputType.type_name)
                .order_by(OutputType.type_name.asc())
            )
        ).all()
        departments = (
            await db.execute(
                select(Department.department_id, Department.department_name, func.count(CoreResearchObject.research_id))
                .join(CoreResearchObject, CoreResearchObject.department_id == Department.department_id)
                .where(Department.is_active.is_(True), *public_filters)
                .group_by(Department.department_id, Department.department_name)
                .order_by(Department.department_name.asc())
            )
        ).all()
        domains = (
            await db.execute(
                select(ResearchDomain.domain_id, ResearchDomain.domain_name, func.count(CoreResearchObjectDomain.research_id))
                .join(CoreResearchObjectDomain, CoreResearchObjectDomain.domain_id == ResearchDomain.domain_id)
                .join(CoreResearchObject, CoreResearchObject.research_id == CoreResearchObjectDomain.research_id)
                .where(ResearchDomain.is_active.is_(True), *public_filters)
                .group_by(ResearchDomain.domain_id, ResearchDomain.domain_name)
                .order_by(ResearchDomain.domain_name.asc())
            )
        ).all()
        keywords = (
            await db.execute(
                select(Keyword.keyword_id, Keyword.keyword_text, func.count(CoreResearchObjectKeyword.research_id))
                .join(CoreResearchObjectKeyword, CoreResearchObjectKeyword.keyword_id == Keyword.keyword_id)
                .join(CoreResearchObject, CoreResearchObject.research_id == CoreResearchObjectKeyword.research_id)
                .where(*public_filters)
                .group_by(Keyword.keyword_id, Keyword.keyword_text)
                .order_by(Keyword.keyword_text.asc())
            )
        ).all()
        authors = (
            await db.execute(
                select(Researcher.researcher_id, Researcher.full_name, func.count(CoreResearchObjectAuthor.research_id))
                .join(CoreResearchObjectAuthor, CoreResearchObjectAuthor.researcher_id == Researcher.researcher_id)
                .join(CoreResearchObject, CoreResearchObject.research_id == CoreResearchObjectAuthor.research_id)
                .where(*public_filters)
                .group_by(Researcher.researcher_id, Researcher.full_name)
                .order_by(Researcher.full_name.asc())
            )
        ).all()
        year_min, year_max = (
            await db.execute(
                select(func.min(CoreResearchObject.year), func.max(CoreResearchObject.year)).where(*public_filters)
            )
        ).one()
        return PublicResearchLookupsOut(
            output_types=[self._to_facet_lookup(id_value, name, int(count)) for id_value, name, count in output_types],
            departments=[self._to_facet_lookup(id_value, name, int(count)) for id_value, name, count in departments],
            domains=[self._to_facet_lookup(id_value, name, int(count)) for id_value, name, count in domains],
            keywords=[self._to_facet_lookup(id_value, name, int(count)) for id_value, name, count in keywords],
            authors=[self._to_facet_lookup(id_value, name, int(count)) for id_value, name, count in authors],
            year_min=year_min,
            year_max=year_max,
        )

    def _to_list_item(self, core_obj: CoreResearchObject) -> PublicResearchListItemOut:
        authors = sorted(core_obj.authors, key=lambda item: item.author_order)
        domains = sorted(core_obj.domains, key=lambda item: item.domain.domain_name)
        keywords = sorted(core_obj.keywords, key=lambda item: item.keyword.keyword_text)
        return PublicResearchListItemOut(
            research_id=core_obj.research_id,
            title=core_obj.title,
            description=core_obj.description,
            cover_image_url=self._cover_image_url(core_obj.research_id),
            year=core_obj.year,
            output_type=self._to_lookup(core_obj.output_type_id, core_obj.output_type.type_name),
            department=self._to_lookup(core_obj.department_id, core_obj.department.department_name),
            authors=[PublicAuthorOut.model_validate(item, from_attributes=True) for item in authors],
            domains=[self._to_lookup(item.domain_id, item.domain.domain_name) for item in domains],
            keywords=[self._to_lookup(item.keyword_id, item.keyword.keyword_text) for item in keywords],
            access_level=core_obj.access_level,
            version_no=core_obj.version_no,
            approved_at=core_obj.approved_at,
            metadata_quality_score=core_obj.metadata_quality_score,
            view_count=core_obj.view_count,
            download_count=core_obj.download_count,
        )

    async def _list_public_researches_postgres(
        self,
        db: AsyncSession,
        *,
        q: str | None,
        output_type_ids: list[UUID] | None,
        department_ids: list[UUID] | None,
        domain_ids: list[UUID] | None,
        keyword_ids: list[UUID] | None,
        author_ids: list[UUID] | None,
        year_from: int | None,
        year_to: int | None,
        has_files: bool,
        sort: str,
        limit: int,
        offset: int,
    ) -> PublicResearchListOut:
        filters = self._filters(
            q=q,
            output_type_ids=output_type_ids,
            department_ids=department_ids,
            domain_ids=domain_ids,
            keyword_ids=keyword_ids,
            author_ids=author_ids,
            year_from=year_from,
            year_to=year_to,
            has_files=has_files,
        )
        total_stmt = select(func.count()).select_from(CoreResearchObject).where(*filters)
        total = int((await db.execute(total_stmt)).scalar_one())

        order_by = {
            "oldest": (CoreResearchObject.approved_at.asc(), CoreResearchObject.created_at.asc()),
            "most_viewed": (CoreResearchObject.view_count.desc(), CoreResearchObject.approved_at.desc()),
            "most_downloaded": (CoreResearchObject.download_count.desc(), CoreResearchObject.approved_at.desc()),
            "title_asc": (func.unaccent(CoreResearchObject.title).asc(), CoreResearchObject.approved_at.desc()),
        }.get(sort, (CoreResearchObject.approved_at.desc(), CoreResearchObject.created_at.desc()))
        stmt = (
            select(CoreResearchObject)
            .options(*self._base_options())
            .where(*filters)
            .order_by(*order_by)
            .offset(offset)
            .limit(limit)
        )
        result = await db.execute(stmt)
        items = [self._to_list_item(core_obj) for core_obj in result.scalars().all()]
        return PublicResearchListOut(items=items, total=total, limit=limit, offset=offset)

    async def list_public_researches(
        self,
        db: AsyncSession,
        *,
        q: str | None,
        output_type_ids: list[UUID] | None,
        department_ids: list[UUID] | None,
        domain_ids: list[UUID] | None,
        keyword_ids: list[UUID] | None,
        author_ids: list[UUID] | None,
        year_from: int | None,
        year_to: int | None,
        has_files: bool,
        sort: str,
        limit: int,
        offset: int,
    ) -> PublicResearchListOut:
        search_or_filter_requested = any(
            value
            for value in (
                q,
                output_type_ids,
                department_ids,
                domain_ids,
                keyword_ids,
                author_ids,
                year_from,
                year_to,
            )
        )
        postgres_kwargs = {
            "q": q,
            "output_type_ids": output_type_ids,
            "department_ids": department_ids,
            "domain_ids": domain_ids,
            "keyword_ids": keyword_ids,
            "author_ids": author_ids,
            "year_from": year_from,
            "year_to": year_to,
            "has_files": has_files,
            "sort": sort,
            "limit": limit,
            "offset": offset,
        }
        if not search_or_filter_requested or has_files:
            return await self._list_public_researches_postgres(
                db,
                **postgres_kwargs,
            )

        try:
            page = await elasticsearch_search_service.search_researches(
                query=q,
                access_filter={"term": {"access_level": AccessLevel.public.value}},
                output_type_ids=output_type_ids,
                department_ids=department_ids,
                domain_ids=domain_ids,
                keyword_ids=keyword_ids,
                author_ids=author_ids,
                year_from=year_from,
                year_to=year_to,
                sort=sort,
                limit=limit,
                offset=offset,
            )
        except ElasticsearchSearchError:
            logger.warning("Elasticsearch public search failed; using PostgreSQL fallback", exc_info=True)
            return await self._list_public_researches_postgres(
                db,
                **postgres_kwargs,
            )

        if not page.hits:
            return PublicResearchListOut(items=[], total=page.total, limit=limit, offset=offset)

        hit_ids = [hit.research_id for hit in page.hits]
        filters = self._filters(
            q=None,
            output_type_ids=output_type_ids,
            department_ids=department_ids,
            domain_ids=domain_ids,
            keyword_ids=keyword_ids,
            author_ids=author_ids,
            year_from=year_from,
            year_to=year_to,
            has_files=False,
        )
        stmt = (
            select(CoreResearchObject)
            .options(*self._base_options())
            .where(CoreResearchObject.research_id.in_(hit_ids), *filters)
        )
        result = await db.execute(stmt)
        objects_by_id = {item.research_id: item for item in result.scalars().all()}
        items = [
            self._to_list_item(objects_by_id[research_id])
            for research_id in hit_ids
            if research_id in objects_by_id
        ]
        return PublicResearchListOut(items=items, total=page.total, limit=limit, offset=offset)

    async def _suggest_public_researches_postgres(
        self,
        db: AsyncSession,
        *,
        q: str,
        limit: int,
    ) -> list[PublicResearchSuggestionOut]:
        pattern = func.unaccent(f"%{q.strip()}%")
        stmt = (
            select(CoreResearchObject)
            .where(
                CoreResearchObject.deleted_at.is_(None),
                CoreResearchObject.is_current.is_(True),
                CoreResearchObject.access_level == AccessLevel.public,
                func.unaccent(CoreResearchObject.title).ilike(pattern),
            )
            .order_by(CoreResearchObject.title.asc())
            .limit(limit)
        )
        items = (await db.execute(stmt)).scalars().all()
        return [
            PublicResearchSuggestionOut(
                research_id=item.research_id,
                title=item.title,
                year=item.year,
            )
            for item in items
        ]

    async def suggest_public_researches(
        self,
        db: AsyncSession,
        *,
        q: str,
        limit: int,
    ) -> list[PublicResearchSuggestionOut]:
        normalized_query = q.strip()
        try:
            page = await elasticsearch_search_service.search_researches(
                query=normalized_query,
                access_filter={"term": {"access_level": AccessLevel.public.value}},
                limit=limit,
                offset=0,
            )
        except ElasticsearchSearchError:
            logger.warning("Elasticsearch suggestions failed; using PostgreSQL fallback", exc_info=True)
            return await self._suggest_public_researches_postgres(
                db,
                q=normalized_query,
                limit=limit,
            )

        if not page.hits:
            return []

        hit_ids = [hit.research_id for hit in page.hits]
        stmt = select(CoreResearchObject).where(
            CoreResearchObject.research_id.in_(hit_ids),
            CoreResearchObject.deleted_at.is_(None),
            CoreResearchObject.is_current.is_(True),
            CoreResearchObject.access_level == AccessLevel.public,
        )
        items = (await db.execute(stmt)).scalars().all()
        items_by_id = {item.research_id: item for item in items}
        return [
            PublicResearchSuggestionOut(
                research_id=items_by_id[research_id].research_id,
                title=items_by_id[research_id].title,
                year=items_by_id[research_id].year,
            )
            for research_id in hit_ids
            if research_id in items_by_id
        ]

    async def get_public_research_detail(self, db: AsyncSession, *, research_id: UUID) -> PublicResearchDetailOut:
        stmt = (
            select(CoreResearchObject)
            .options(*self._base_options())
            .where(CoreResearchObject.research_id == research_id)
            .where(CoreResearchObject.deleted_at.is_(None))
            .where(CoreResearchObject.access_level == AccessLevel.public)
        )
        result = await db.execute(stmt)
        core_obj = result.scalar_one_or_none()
        if core_obj is None:
            raise NotFoundException("Không tìm thấy bài nghiên cứu public")

        core_obj.view_count = (
            await db.execute(
                update(CoreResearchObject)
                .where(CoreResearchObject.research_id == research_id)
                .values(view_count=CoreResearchObject.view_count + 1)
                .returning(CoreResearchObject.view_count)
            )
        ).scalar_one()

        active_public_files = [
            item
            for item in sorted(core_obj.file_attachments, key=lambda file: file.uploaded_at, reverse=True)
            if item.file_status == FileStatus.active and item.access_level == AccessLevel.public
        ]
        return PublicResearchDetailOut(
            **self._to_list_item(core_obj).model_dump(),
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
            file_attachments=[PublicFileOut.model_validate(item, from_attributes=True) for item in active_public_files],
        )

    async def create_download_url(
        self,
        db: AsyncSession,
        *,
        research_id: UUID,
        file_id: UUID,
    ) -> PublicResearchDownloadOut:
        stmt = (
            select(CoreFileAttachment)
            .join(CoreResearchObject, CoreResearchObject.research_id == CoreFileAttachment.research_id)
            .where(CoreResearchObject.research_id == research_id)
            .where(CoreResearchObject.deleted_at.is_(None))
            .where(CoreResearchObject.access_level == AccessLevel.public)
            .where(CoreFileAttachment.file_id == file_id)
            .where(CoreFileAttachment.file_status == FileStatus.active)
            .where(CoreFileAttachment.access_level == AccessLevel.public)
        )
        result = await db.execute(stmt)
        file_obj = result.scalar_one_or_none()
        if file_obj is None:
            raise NotFoundException("Không tìm thấy file public")
        if file_obj.mime_type != "application/pdf" and file_obj.file_extension != ".pdf":
            raise BadRequestException("Chỉ hỗ trợ download file PDF")

        download_url = create_presigned_download_url(
            object_key=file_obj.storage_path,
            filename=file_obj.original_filename,
            expires_in=DOWNLOAD_URL_TTL_SECONDS,
        )
        await db.execute(
            update(CoreResearchObject)
            .where(CoreResearchObject.research_id == research_id)
            .values(download_count=CoreResearchObject.download_count + 1)
        )

        return PublicResearchDownloadOut(
            download_url=download_url,
            expires_in=DOWNLOAD_URL_TTL_SECONDS,
        )


public_research_service = PublicResearchService()
