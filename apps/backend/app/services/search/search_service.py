from uuid import UUID

from sqlalchemy import Float, String, cast, exists, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.core.core_research_object import CoreResearchObject
from app.models.core.core_research_object_domain import CoreResearchObjectDomain
from app.models.core.core_research_object_keyword import CoreResearchObjectKeyword
from app.models.auth.user import User
from app.models.enum import AccessLevel, WorkflowStatus
from app.models.reference.keyword import Keyword
from app.models.reference.research_domain import ResearchDomain
from app.models.staging.stg_research_object import StgResearchObject
from app.models.staging.stg_research_object_author import StgResearchObjectAuthor
from app.models.staging.stg_research_object_domain import StgResearchObjectDomain
from app.models.staging.stg_research_object_keyword import StgResearchObjectKeyword
from app.schemas.search import (
    CoreSearchResponseOut,
    CoreSearchResultOut,
    StagingSearchResponseOut,
    StagingSearchResultOut,
)


class SearchService:
    @staticmethod
    def _unaccent_ilike(column, pattern):
        return func.unaccent(func.coalesce(column, "")).ilike(pattern)

    @staticmethod
    def _access_filter(current_user: User | None):
        if current_user is None or current_user.role is None:
            return CoreResearchObject.access_level == AccessLevel.public

        role_code = current_user.role.role_code
        if role_code == "SUPER_ADMIN" or role_code == "MANAGER":
            return True
        if role_code == "DATA_ENTRY":
            return or_(
                CoreResearchObject.access_level == AccessLevel.public,
                CoreResearchObject.source_staging_id.in_(
                    select(StgResearchObject.staging_id).where(StgResearchObject.created_by == current_user.user_id)
                ),
                CoreResearchObject.research_id.in_(
                    select(StgResearchObject.source_core_research_id).where(
                        StgResearchObject.created_by == current_user.user_id
                    )
                ),
            )
        if role_code == "REVIEWER":
            return or_(
                CoreResearchObject.access_level.in_([AccessLevel.public, AccessLevel.internal]),
                CoreResearchObject.research_id.in_(
                    select(StgResearchObject.source_core_research_id).where(
                        StgResearchObject.workflow_status == WorkflowStatus.pending_review
                    )
                ),
            )
        if role_code == "APPROVER":
            return or_(
                CoreResearchObject.access_level.in_([AccessLevel.public, AccessLevel.internal]),
                CoreResearchObject.research_id.in_(
                    select(StgResearchObject.source_core_research_id).where(
                        StgResearchObject.workflow_status == WorkflowStatus.pending_approval
                    )
                ),
            )
        return CoreResearchObject.access_level == AccessLevel.public

    @staticmethod
    def _staging_access_filter(current_user: User):
        role_code = current_user.role.role_code if current_user.role else None
        if role_code in {"SUPER_ADMIN", "MANAGER"}:
            return True
        if role_code == "DATA_ENTRY":
            return StgResearchObject.created_by == current_user.user_id
        if role_code == "REVIEWER":
            return StgResearchObject.workflow_status == WorkflowStatus.pending_review
        if role_code == "APPROVER":
            return StgResearchObject.workflow_status == WorkflowStatus.pending_approval
        return False

    @staticmethod
    def _core_category_filters(
        *,
        output_type_ids: list[UUID] | None,
        department_ids: list[UUID] | None,
        domain_ids: list[UUID] | None,
        keyword_ids: list[UUID] | None,
    ):
        filters = []
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
        return filters

    @staticmethod
    def _staging_category_filters(
        *,
        output_type_ids: list[UUID] | None,
        department_ids: list[UUID] | None,
        domain_ids: list[UUID] | None,
        keyword_ids: list[UUID] | None,
    ):
        filters = []
        if output_type_ids:
            filters.append(StgResearchObject.output_type_id.in_(output_type_ids))
        if department_ids:
            filters.append(StgResearchObject.department_id.in_(department_ids))
        if domain_ids:
            filters.append(
                exists()
                .where(StgResearchObjectDomain.staging_id == StgResearchObject.staging_id)
                .where(StgResearchObjectDomain.domain_id.in_(domain_ids))
            )
        if keyword_ids:
            filters.append(
                exists()
                .where(StgResearchObjectKeyword.staging_id == StgResearchObject.staging_id)
                .where(StgResearchObjectKeyword.keyword_id.in_(keyword_ids))
            )
        return filters

    @staticmethod
    def _staging_search_vector():
        author_text = (
            select(func.string_agg(func.concat_ws(" ", StgResearchObjectAuthor.full_name, StgResearchObjectAuthor.email), " "))
            .where(StgResearchObjectAuthor.staging_id == StgResearchObject.staging_id)
            .correlate(StgResearchObject)
            .scalar_subquery()
        )
        keyword_text = (
            select(func.string_agg(Keyword.keyword_text, " "))
            .select_from(StgResearchObjectKeyword)
            .join(Keyword, Keyword.keyword_id == StgResearchObjectKeyword.keyword_id)
            .where(StgResearchObjectKeyword.staging_id == StgResearchObject.staging_id)
            .correlate(StgResearchObject)
            .scalar_subquery()
        )
        domain_text = (
            select(func.string_agg(ResearchDomain.domain_name, " "))
            .select_from(StgResearchObjectDomain)
            .join(ResearchDomain, ResearchDomain.domain_id == StgResearchObjectDomain.domain_id)
            .where(StgResearchObjectDomain.staging_id == StgResearchObject.staging_id)
            .correlate(StgResearchObject)
            .scalar_subquery()
        )
        document = func.concat_ws(
            " ",
            StgResearchObject.title,
            StgResearchObject.description,
            StgResearchObject.abstract,
            StgResearchObject.publisher,
            StgResearchObject.identifier,
            cast(StgResearchObject.year, String),
            author_text,
            keyword_text,
            domain_text,
        )
        return func.to_tsvector("simple", func.unaccent(func.coalesce(document, "")))

    async def search_core_postgres(
        self,
        db: AsyncSession,
        *,
        query: str,
        output_type_ids: list[UUID] | None = None,
        department_ids: list[UUID] | None = None,
        domain_ids: list[UUID] | None = None,
        keyword_ids: list[UUID] | None = None,
        limit: int,
        offset: int,
        current_user: User | None = None,
    ) -> CoreSearchResponseOut:
        normalized_query = query.strip()
        if not normalized_query:
            return CoreSearchResponseOut(items=[], total=0, limit=limit, offset=offset)

        ts_query = func.websearch_to_tsquery("simple", func.unaccent(normalized_query))
        search_vector = func.coalesce(CoreResearchObject.search_vector, func.to_tsvector("simple", ""))
        rank = cast(func.ts_rank_cd(search_vector, ts_query), Float)
        ilike_pattern = func.unaccent(f"%{normalized_query}%")

        filters = [
            CoreResearchObject.deleted_at.is_(None),
            self._access_filter(current_user),
            or_(
                search_vector.op("@@")(ts_query),
                self._unaccent_ilike(CoreResearchObject.identifier, ilike_pattern),
            ),
            *self._core_category_filters(
                output_type_ids=output_type_ids,
                department_ids=department_ids,
                domain_ids=domain_ids,
                keyword_ids=keyword_ids,
            ),
        ]
        total_stmt = select(func.count()).select_from(CoreResearchObject).where(*filters)
        total = int((await db.execute(total_stmt)).scalar_one())

        stmt = (
            select(CoreResearchObject, rank.label("rank"))
            .where(*filters)
            .order_by(rank.desc(), CoreResearchObject.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await db.execute(stmt)

        rows: list[CoreSearchResultOut] = []
        for core_obj, score in result.all():
            rows.append(
                CoreSearchResultOut(
                    research_id=core_obj.research_id,
                    title=core_obj.title,
                    year=core_obj.year,
                    access_level=core_obj.access_level,
                    version_no=core_obj.version_no,
                    approved_at=core_obj.approved_at,
                    rank=float(score or 0.0),
                )
            )
        return CoreSearchResponseOut(items=rows, total=total, limit=limit, offset=offset)

    async def search_staging_postgres(
        self,
        db: AsyncSession,
        *,
        query: str,
        workflow_statuses: list[WorkflowStatus] | None = None,
        output_type_ids: list[UUID] | None = None,
        department_ids: list[UUID] | None = None,
        domain_ids: list[UUID] | None = None,
        keyword_ids: list[UUID] | None = None,
        limit: int,
        offset: int,
        current_user: User,
    ) -> StagingSearchResponseOut:
        normalized_query = query.strip()
        if not normalized_query:
            return StagingSearchResponseOut(items=[], total=0, limit=limit, offset=offset)

        ts_query = func.websearch_to_tsquery("simple", func.unaccent(normalized_query))
        search_vector = self._staging_search_vector()
        rank = cast(func.ts_rank_cd(search_vector, ts_query), Float)
        ilike_pattern = func.unaccent(f"%{normalized_query}%")

        filters = [
            StgResearchObject.deleted_at.is_(None),
            self._staging_access_filter(current_user),
            or_(
                search_vector.op("@@")(ts_query),
                self._unaccent_ilike(StgResearchObject.identifier, ilike_pattern),
            ),
            *self._staging_category_filters(
                output_type_ids=output_type_ids,
                department_ids=department_ids,
                domain_ids=domain_ids,
                keyword_ids=keyword_ids,
            ),
        ]
        if workflow_statuses:
            filters.append(StgResearchObject.workflow_status.in_(workflow_statuses))

        total_stmt = select(func.count()).select_from(StgResearchObject).where(*filters)
        total = int((await db.execute(total_stmt)).scalar_one())

        stmt = (
            select(StgResearchObject, rank.label("rank"))
            .where(*filters)
            .order_by(rank.desc(), StgResearchObject.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await db.execute(stmt)

        rows: list[StagingSearchResultOut] = []
        for staging_obj, score in result.all():
            rows.append(
                StagingSearchResultOut(
                    staging_id=staging_obj.staging_id,
                    title=staging_obj.title,
                    output_type_id=staging_obj.output_type_id,
                    department_id=staging_obj.department_id,
                    year=staging_obj.year,
                    workflow_status=staging_obj.workflow_status,
                    access_level=staging_obj.access_level,
                    source_core_research_id=staging_obj.source_core_research_id,
                    created_by=staging_obj.created_by,
                    created_at=staging_obj.created_at,
                    updated_at=staging_obj.updated_at,
                    rank=float(score or 0.0),
                )
            )
        return StagingSearchResponseOut(items=rows, total=total, limit=limit, offset=offset)


search_service = SearchService()
