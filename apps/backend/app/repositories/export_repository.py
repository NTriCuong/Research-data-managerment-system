from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.core.core_research_object import CoreResearchObject
from app.models.core.core_research_object_author import CoreResearchObjectAuthor
from app.models.core.core_research_object_domain import CoreResearchObjectDomain
from app.models.enum import WorkflowStatus
from app.models.reference.department import Department
from app.models.reference.researcher import Researcher
from app.models.staging.stg_research_object import StgResearchObject
from app.models.staging.stg_research_object_author import StgResearchObjectAuthor


class ExportRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
# researcher
    async def get_researcher(self, researcher_id: UUID) -> Researcher | None:
        result = await self.db.execute(
            select(Researcher)
            .options(selectinload(Researcher.department))
            .where(Researcher.researcher_id == researcher_id)
        )
        return result.scalar_one_or_none()

    async def count_total_researches(self, researcher_id: UUID) -> int:
        result = await self.db.execute(
            select(func.count(func.distinct(StgResearchObject.staging_id)))
            .select_from(StgResearchObject)
            .join(StgResearchObjectAuthor, StgResearchObjectAuthor.staging_id == StgResearchObject.staging_id)
            .where(StgResearchObjectAuthor.researcher_id == researcher_id)
            .where(StgResearchObject.deleted_at.is_(None))
        )
        return result.scalar_one()

    async def count_pending_researches(self, researcher_id: UUID) -> int:
        result = await self.db.execute(
            select(func.count(func.distinct(StgResearchObject.staging_id)))
            .select_from(StgResearchObject)
            .join(StgResearchObjectAuthor, StgResearchObjectAuthor.staging_id == StgResearchObject.staging_id)
            .where(StgResearchObjectAuthor.researcher_id == researcher_id)
            .where(StgResearchObject.deleted_at.is_(None))
            .where(
                StgResearchObject.workflow_status.in_(
                    (WorkflowStatus.pending_review, WorkflowStatus.pending_approval)
                )
            )
        )
        return result.scalar_one()

    async def count_rejected_researches(self, researcher_id: UUID) -> int:
        result = await self.db.execute(
            select(func.count(func.distinct(StgResearchObject.staging_id)))
            .select_from(StgResearchObject)
            .join(StgResearchObjectAuthor, StgResearchObjectAuthor.staging_id == StgResearchObject.staging_id)
            .where(StgResearchObjectAuthor.researcher_id == researcher_id)
            .where(StgResearchObject.deleted_at.is_(None))
            .where(StgResearchObject.workflow_status == WorkflowStatus.rejected)
        )
        return result.scalar_one()

    async def count_published_researches(self, researcher_id: UUID) -> int:
        result = await self.db.execute(
            select(func.count(func.distinct(CoreResearchObject.research_id)))
            .select_from(CoreResearchObject)
            .join(CoreResearchObjectAuthor, CoreResearchObjectAuthor.research_id == CoreResearchObject.research_id)
            .where(CoreResearchObjectAuthor.researcher_id == researcher_id)
            .where(CoreResearchObject.deleted_at.is_(None))
            .where(CoreResearchObject.is_current.is_(True))
        )
        return result.scalar_one()
# list research trong năm

    async def list_researches_by_year(self, year: int) -> list[CoreResearchObject]:
        result = await self.db.execute(
            select(CoreResearchObject)
            .select_from(CoreResearchObject)
            .where(func.date_part("year", CoreResearchObject.created_at) == year)
            .where(CoreResearchObject.deleted_at.is_(None))
            .where(CoreResearchObject.is_current.is_(True))
            .order_by(CoreResearchObject.created_at.desc())
        )
        return result.scalars().all()

# khoa
    async def get_department(self, department_id: UUID) -> Department | None:
        result = await self.db.execute(
            select(Department).where(Department.department_id == department_id)
        )
        return result.scalar_one_or_none()

# list research theo khoa
    async def list_researches_by_department(self, department_id: UUID) -> list[CoreResearchObject]:
        result = await self.db.execute(
            select(CoreResearchObject)
            .select_from(CoreResearchObject)
            .where(CoreResearchObject.department_id == department_id)
            .where(CoreResearchObject.deleted_at.is_(None))
            .where(CoreResearchObject.is_current.is_(True))
            .options(
                selectinload(CoreResearchObject.output_type),
                selectinload(CoreResearchObject.department),
                selectinload(CoreResearchObject.domains).selectinload(CoreResearchObjectDomain.domain),
                selectinload(CoreResearchObject.authors),
            )
            .order_by(CoreResearchObject.created_at.desc())
        )
        return result.scalars().all()

# list research theo khoa trong năm
    async def list_researches_by_department_and_year(self, department_id: UUID, year: int) -> list[CoreResearchObject]:
        result = await self.db.execute(
            select(CoreResearchObject)
            .select_from(CoreResearchObject)
            .where(CoreResearchObject.department_id == department_id)
            .where(func.date_part("year", CoreResearchObject.created_at) == year)
            .where(CoreResearchObject.deleted_at.is_(None))
            .where(CoreResearchObject.is_current.is_(True))
            .options(
                selectinload(CoreResearchObject.output_type),
                selectinload(CoreResearchObject.department),
                selectinload(CoreResearchObject.domains).selectinload(CoreResearchObjectDomain.domain),
                selectinload(CoreResearchObject.authors),
            )
            .order_by(CoreResearchObject.created_at.desc())
        )
        return result.scalars().all()

# list research theo researcher
    async def list_researches_by_researcher(self, researcher_id: UUID) -> list[CoreResearchObject]:
        result = await self.db.execute(
            select(CoreResearchObject)
            .select_from(CoreResearchObject)
            .join(CoreResearchObjectAuthor, CoreResearchObjectAuthor.research_id == CoreResearchObject.research_id)
            .where(CoreResearchObjectAuthor.researcher_id == researcher_id)
            .where(CoreResearchObject.deleted_at.is_(None))
            .where(CoreResearchObject.is_current.is_(True))
            .options(
                selectinload(CoreResearchObject.output_type),
                selectinload(CoreResearchObject.department),
                selectinload(CoreResearchObject.domains).selectinload(CoreResearchObjectDomain.domain),
                selectinload(CoreResearchObject.authors),
            )
            .order_by(CoreResearchObject.created_at.desc())
        )
        return result.unique().scalars().all()