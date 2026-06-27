from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth.user import User
from app.models.enum import WorkflowStatus
from app.models.staging.stg_research_object import StgResearchObject


class StagingReviewRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, staging_id: UUID) -> StgResearchObject | None:
        result = await self.db.execute(
            select(StgResearchObject).where(StgResearchObject.staging_id == staging_id)
        )
        return result.scalar_one_or_none()

    async def list_pending_review_records(self, *, limit: int = 20, offset: int = 0) -> list[StgResearchObject]:
        result = await self.db.execute(
            select(StgResearchObject)
            .where(StgResearchObject.workflow_status == WorkflowStatus.pending_review)
            .where(StgResearchObject.deleted_at.is_(None))
            .order_by(StgResearchObject.submitted_at.desc().nullslast(), StgResearchObject.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_approvers(self) -> list[User]:
        result = await self.db.execute(
            select(User).where(User.role.has(role_code="APPROVER"))
        )
        return result.scalars().all()
