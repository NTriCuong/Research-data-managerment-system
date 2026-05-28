from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.core.core_research_object import CoreResearchObject
from app.models.enum import WorkflowStatus
from app.models.staging.stg_research_object import StgResearchObject


class CoreApproveRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_staging_by_id(self, staging_id: UUID, *, with_relations: bool = False) -> StgResearchObject | None:
        stmt = select(StgResearchObject).where(StgResearchObject.staging_id == staging_id)
        if with_relations:
            stmt = stmt.options(
                selectinload(StgResearchObject.authors),
                selectinload(StgResearchObject.domains),
                selectinload(StgResearchObject.keywords),
                selectinload(StgResearchObject.file_attachments),
            )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_pending_approval_records(self, *, limit: int = 20, offset: int = 0) -> list[StgResearchObject]:
        result = await self.db.execute(
            select(StgResearchObject)
            .where(StgResearchObject.workflow_status == WorkflowStatus.pending_approval)
            .where(StgResearchObject.deleted_at.is_(None))
            .order_by(StgResearchObject.reviewed_at.desc().nullslast(), StgResearchObject.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_core_by_id(self, research_id: UUID, *, with_relations: bool = False) -> CoreResearchObject | None:
        stmt = select(CoreResearchObject).where(CoreResearchObject.research_id == research_id)
        if with_relations:
            stmt = stmt.options(
                selectinload(CoreResearchObject.authors),
                selectinload(CoreResearchObject.domains),
                selectinload(CoreResearchObject.keywords),
                selectinload(CoreResearchObject.file_attachments),
            )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
