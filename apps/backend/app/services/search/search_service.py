from sqlalchemy import Float, cast, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.core.core_research_object import CoreResearchObject
from app.models.auth.user import User
from app.models.enum import AccessLevel, WorkflowStatus
from app.models.staging.stg_research_object import StgResearchObject
from app.schemas.core_approve import CoreSearchResponseOut, CoreSearchResultOut


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

    async def search_core_postgres(
        self,
        db: AsyncSession,
        *,
        query: str,
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


search_service = SearchService()
