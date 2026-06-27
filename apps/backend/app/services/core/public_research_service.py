from uuid import UUID

from sqlalchemy import exists, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import BadRequestException, NotFoundException
from app.core.config import settings
from app.models.core.core_file_attachment import CoreFileAttachment
from app.models.core.core_research_object import CoreResearchObject
from app.models.core.core_research_object_domain import CoreResearchObjectDomain
from app.models.core.core_research_object_keyword import CoreResearchObjectKeyword
from app.models.enum import AccessLevel, FileStatus
from app.models.reference.department import Department
from app.models.reference.keyword import Keyword
from app.models.reference.output_type import OutputType
from app.models.reference.research_domain import ResearchDomain
from app.schemas.public_research import (
    PublicAuthorOut,
    PublicFileOut,
    PublicLookupOut,
    PublicResearchDetailOut,
    PublicResearchDownloadOut,
    PublicResearchLookupsOut,
    PublicResearchListItemOut,
    PublicResearchListOut,
)
from app.services.storage.r2_storage import create_presigned_download_url


DOWNLOAD_URL_TTL_SECONDS = 300


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
        output_type_id: UUID | None,
        department_id: UUID | None,
        domain_id: UUID | None,
        keyword_id: UUID | None,
        year: int | None,
    ):
        filters = [
            CoreResearchObject.deleted_at.is_(None),
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
                )
            )
        if output_type_id:
            filters.append(CoreResearchObject.output_type_id == output_type_id)
        if department_id:
            filters.append(CoreResearchObject.department_id == department_id)
        if domain_id:
            filters.append(
                exists()
                .where(CoreResearchObjectDomain.research_id == CoreResearchObject.research_id)
                .where(CoreResearchObjectDomain.domain_id == domain_id)
            )
        if keyword_id:
            filters.append(
                exists()
                .where(CoreResearchObjectKeyword.research_id == CoreResearchObject.research_id)
                .where(CoreResearchObjectKeyword.keyword_id == keyword_id)
            )
        if year:
            filters.append(CoreResearchObject.year == year)
        return filters

    @staticmethod
    def _to_lookup(id_value: UUID, name: str) -> PublicLookupOut:
        return PublicLookupOut(id=id_value, name=name)

    @staticmethod
    def _cover_image_url(research_id: UUID) -> str | None:
        if not settings.CLOUDFLARE_R2_PUBLIC_BASE_URL:
            return None
        base_url = settings.CLOUDFLARE_R2_PUBLIC_BASE_URL.rstrip("/")
        return f"{base_url}/public/research-covers/{research_id}.jpg"

    async def get_public_lookups(self, db: AsyncSession) -> PublicResearchLookupsOut:
        output_types = (
            await db.execute(
                select(OutputType)
                .where(OutputType.is_active.is_(True))
                .order_by(OutputType.type_name.asc())
            )
        ).scalars().all()
        departments = (
            await db.execute(
                select(Department)
                .where(Department.is_active.is_(True))
                .order_by(Department.department_name.asc())
            )
        ).scalars().all()
        domains = (
            await db.execute(
                select(ResearchDomain)
                .where(ResearchDomain.is_active.is_(True))
                .order_by(ResearchDomain.domain_name.asc())
            )
        ).scalars().all()
        keywords = (await db.execute(select(Keyword).order_by(Keyword.keyword_text.asc()))).scalars().all()
        return PublicResearchLookupsOut(
            output_types=[self._to_lookup(item.output_type_id, item.type_name) for item in output_types],
            departments=[self._to_lookup(item.department_id, item.department_name) for item in departments],
            domains=[self._to_lookup(item.domain_id, item.domain_name) for item in domains],
            keywords=[self._to_lookup(item.keyword_id, item.keyword_text) for item in keywords],
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
        )

    async def list_public_researches(
        self,
        db: AsyncSession,
        *,
        q: str | None,
        output_type_id: UUID | None,
        department_id: UUID | None,
        domain_id: UUID | None,
        keyword_id: UUID | None,
        year: int | None,
        limit: int,
        offset: int,
    ) -> PublicResearchListOut:
        filters = self._filters(
            q=q,
            output_type_id=output_type_id,
            department_id=department_id,
            domain_id=domain_id,
            keyword_id=keyword_id,
            year=year,
        )
        total_stmt = select(func.count()).select_from(CoreResearchObject).where(*filters)
        total = int((await db.execute(total_stmt)).scalar_one())

        stmt = (
            select(CoreResearchObject)
            .options(*self._base_options())
            .where(*filters)
            .order_by(CoreResearchObject.approved_at.desc(), CoreResearchObject.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await db.execute(stmt)
        items = [self._to_list_item(core_obj) for core_obj in result.scalars().all()]
        return PublicResearchListOut(items=items, total=total, limit=limit, offset=offset)

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

        return PublicResearchDownloadOut(
            download_url=create_presigned_download_url(
                object_key=file_obj.storage_path,
                filename=file_obj.original_filename,
                expires_in=DOWNLOAD_URL_TTL_SECONDS,
            ),
            expires_in=DOWNLOAD_URL_TTL_SECONDS,
        )


public_research_service = PublicResearchService()
