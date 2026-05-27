from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.core.core_research_object import CoreResearchObject
from app.models.enum import WorkflowStatus
from app.models.staging.stg_file_attachment import StgFileAttachment
from app.models.staging.stg_research_object import StgResearchObject


class StagingRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, obj: StgResearchObject) -> StgResearchObject:
        self.db.add(obj)
        await self.db.flush()
        return obj

    async def get_by_id(self, staging_id: UUID, *, with_relations: bool = False) -> StgResearchObject | None:
        stmt = select(StgResearchObject).where(StgResearchObject.staging_id == staging_id)
        if with_relations:
            stmt = stmt.options(
                selectinload(StgResearchObject.domains),
                selectinload(StgResearchObject.keywords),
                selectinload(StgResearchObject.authors),
            )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_creator(
        self,
        *,
        creator_id: UUID,
        workflow_status: WorkflowStatus | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[StgResearchObject]:
        stmt = (
            select(StgResearchObject)
            .where(StgResearchObject.created_by == creator_id)
            .where(StgResearchObject.deleted_at.is_(None))
            .order_by(StgResearchObject.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        if workflow_status is not None:
            stmt = stmt.where(StgResearchObject.workflow_status == workflow_status)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_core_by_id_with_relations(self, research_id: UUID) -> CoreResearchObject | None:
        result = await self.db.execute(
            select(CoreResearchObject)
            .options(
                selectinload(CoreResearchObject.domains),
                selectinload(CoreResearchObject.keywords),
                selectinload(CoreResearchObject.authors),
            )
            .where(CoreResearchObject.research_id == research_id)
            .where(CoreResearchObject.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def add_file_attachment(self, file_obj: StgFileAttachment) -> StgFileAttachment:
        self.db.add(file_obj)
        await self.db.flush()
        return file_obj
