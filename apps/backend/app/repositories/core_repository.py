from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.core.core_research_object import CoreResearchObject


class CoreRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_core_records(self, *, limit: int = 20, offset: int = 0) -> list[CoreResearchObject]:
        result = await self.db.execute(
            select(CoreResearchObject)
            .where(CoreResearchObject.deleted_at.is_(None))
            .order_by(CoreResearchObject.approved_at.desc(), CoreResearchObject.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_core_record(self, research_id: UUID, *, with_relations: bool = False) -> CoreResearchObject | None:
        stmt = (
            select(CoreResearchObject)
            .where(CoreResearchObject.research_id == research_id)
            .where(CoreResearchObject.deleted_at.is_(None))
        )
        if with_relations:
            stmt = stmt.options(
                selectinload(CoreResearchObject.authors),
                selectinload(CoreResearchObject.domains),
                selectinload(CoreResearchObject.keywords),
                selectinload(CoreResearchObject.file_attachments),
                selectinload(CoreResearchObject.metadata_versions),
            )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
