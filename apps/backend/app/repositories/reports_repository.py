from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.core.core_research_object import CoreResearchObject
from app.models.enum import WorkflowStatus
from app.models.reference.department import Department
from app.models.reference.researcher import Researcher
from app.models.staging.stg_research_object import StgResearchObject


class ReportsRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def count_core_repositories(self) -> int:
        result = await self.db.execute(
            select(func.count())
            .select_from(CoreResearchObject)
            .where(CoreResearchObject.deleted_at.is_(None))
            .where(CoreResearchObject.is_current.is_(True))
        )
        return result.scalar_one()

    async def count_staging_by_status(self, status: WorkflowStatus) -> int:
        result = await self.db.execute(
            select(func.count())
            .select_from(StgResearchObject)
            .where(StgResearchObject.deleted_at.is_(None))
            .where(StgResearchObject.workflow_status == status)
        )
        return result.scalar_one()

    async def count_researchers(self) -> int:
        result = await self.db.execute(select(func.count()).select_from(Researcher))
        return result.scalar_one()

    async def count_researchers_by_internal(self, is_internal: bool) -> int:
        result = await self.db.execute(
            select(func.count())
            .select_from(Researcher)
            .where(Researcher.is_internal.is_(is_internal))
        )
        return result.scalar_one()

    async def get_metadata_quality_stats(self) -> dict:
        result = await self.db.execute(
            select(
                func.avg(CoreResearchObject.metadata_quality_score).label("avg_score"),
                func.min(CoreResearchObject.metadata_quality_score).label("min_score"),
                func.max(CoreResearchObject.metadata_quality_score).label("max_score"),
                func.count().label("total"),
            )
            .where(CoreResearchObject.deleted_at.is_(None))
            .where(CoreResearchObject.is_current.is_(True))
        )
        row = result.one()
        return {
            "avg_score": float(row.avg_score) if row.avg_score is not None else 0.0,
            "min_score": float(row.min_score) if row.min_score is not None else 0.0,
            "max_score": float(row.max_score) if row.max_score is not None else 0.0,
            "total_records": row.total,
        }

    async def count_staging_group_by_status(self) -> list[dict]:
        result = await self.db.execute(
            select(
                StgResearchObject.workflow_status.label("status"),
                func.count().label("count"),
            )
            .where(StgResearchObject.deleted_at.is_(None))
            .group_by(StgResearchObject.workflow_status)
            .order_by(func.count().desc())
        )
        return [{"status": row.status, "count": row.count} for row in result.all()]

    async def top_contributing_departments(self, *, limit: int) -> list[dict]:
        result = await self.db.execute(
            select(
                Department.department_name.label("department_name"),
                func.count(CoreResearchObject.research_id).label("count"),
            )
            .join(Department, CoreResearchObject.department_id == Department.department_id)
            .where(CoreResearchObject.deleted_at.is_(None))
            .where(CoreResearchObject.is_current.is_(True))
            .group_by(Department.department_id, Department.department_name)
            .order_by(func.count(CoreResearchObject.research_id).desc())
            .limit(limit)
        )
        return [{"department_name": row.department_name, "count": row.count} for row in result.all()]
