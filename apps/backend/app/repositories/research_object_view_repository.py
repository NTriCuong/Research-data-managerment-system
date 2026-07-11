# app/repositories/research_object_view_repository.py
import uuid

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.logs.research_object_views import ResearchObjectView
from app.models.core.core_research_object import CoreResearchObject
from app.models.core.core_research_object_domain import CoreResearchObjectDomain


class ResearchObjectViewRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

# add lượt xem
    async def add_view(self, research_id: uuid.UUID) -> ResearchObjectView:
        view = ResearchObjectView(research_id=research_id)
        self.session.add(view)
        await self.session.flush()
        return view
    
# Tổng số lượt xem của research_id.
    async def count_views(self, research_id: uuid.UUID) -> int:
        stmt = (
            select(func.count())
            .select_from(ResearchObjectView)
            .where(ResearchObjectView.research_id == research_id)
        )
        return await self.session.scalar(stmt) or 0
# lượt xem từng tháng trong năm=?
#         [
#             {"month": 5, "count": 12},
#             {"month": 6, "count": 30},
#             {"month": 7, "count": 42},
#         ]
    async def count_views_by_month(
        self, research_id: uuid.UUID, year: int
    ) -> list[dict]:
        stmt = (
            select(
                ResearchObjectView.viewed_month.label("month"),
                func.count().label("count"),
            )
            .where(
                ResearchObjectView.research_id == research_id,
                ResearchObjectView.viewed_year == year,
            )
            .group_by(ResearchObjectView.viewed_month)
            .order_by(ResearchObjectView.viewed_month.asc())
        )
        result = await self.session.execute(stmt)
        return [
            {"month": row.month, "count": row.count}
            for row in result.all()
        ]
# lượt xem trong năm
# [
#             {"year": 2024, "count": 120},
#             {"year": 2025, "count": 340},
#             {"year": 2026, "count": 84},
#         ]
    async def count_views_by_year(
        self, research_id: uuid.UUID
    ) -> list[dict]:
        stmt = (
            select(
                ResearchObjectView.viewed_year.label("year"),
                func.count().label("count"),
            )
            .where(ResearchObjectView.research_id == research_id)
            .group_by(ResearchObjectView.viewed_year)
            .order_by(ResearchObjectView.viewed_year.asc())
        )
        result = await self.session.execute(stmt)
        return [
            {"year": row.year, "count": row.count}
            for row in result.all()
        ]
    
    # top research lượt xem nhiều nhất tháng
    async def top10_views_by_month(
        self,
        year: int,
        month: int,
        limit: int = 10,
    ) -> list[dict]:
        stmt = (
            select(
                CoreResearchObject.research_id,
                CoreResearchObject.title,
                func.count(ResearchObjectView.view_id).label("views"),
            )
            .join(
                ResearchObjectView,
                ResearchObjectView.research_id == CoreResearchObject.research_id,
            )
            .where(
                ResearchObjectView.viewed_year == year,
                ResearchObjectView.viewed_month == month,
            )
            .group_by(
                CoreResearchObject.research_id,
                CoreResearchObject.title,
            )
            .order_by(desc("views"))
            .limit(limit)
        )

        result = await self.session.execute(stmt)

        return [
            {
                "research_id": row.research_id,
                "title": row.title,
                "views": row.views,
            }
            for row in result.all()
        ]

    # top research lượt xem nhiều nhất năm 
    async def top10_views_by_year(
        self,
        year: int,
        limit: int = 10,
    ) -> list[dict]:
        stmt = (
            select(
                CoreResearchObject.research_id,
                CoreResearchObject.title,
                func.count(ResearchObjectView.view_id).label("views"),
            )
            .join(
                ResearchObjectView,
                ResearchObjectView.research_id == CoreResearchObject.research_id,
            )
            .where(
                ResearchObjectView.viewed_year == year,
            )
            .group_by(
                CoreResearchObject.research_id,
                CoreResearchObject.title,
            )
            .order_by(desc("views"))
            .limit(limit)
        )

        result = await self.session.execute(stmt)

        return [
            {
                "research_id": row.research_id,
                "title": row.title,
                "views": row.views,
            }
            for row in result.all()
        ]

    # top research theo từng lĩnh vực
    async def top10_views_by_domain(
        self,
        domain_id: uuid.UUID,
        year: int,
        limit: int = 10,
    ) -> list[dict]:

        stmt = (
            select(
                CoreResearchObject.research_id,
                CoreResearchObject.title,
                func.count(ResearchObjectView.view_id).label("views"),
            )
            .join(
                CoreResearchObjectDomain,
                CoreResearchObject.research_id
                == CoreResearchObjectDomain.research_id,
            )
            .join(
                ResearchObjectView,
                CoreResearchObject.research_id
                == ResearchObjectView.research_id,
            )
            .where(
                CoreResearchObjectDomain.domain_id == domain_id,
                ResearchObjectView.viewed_year == year,
            )
            .group_by(
                CoreResearchObject.research_id,
                CoreResearchObject.title,
            )
            .order_by(desc("views"))
            .limit(limit)
        )

        result = await self.session.execute(stmt)

        return [
            {
                "research_id": row.research_id,
                "title": row.title,
                "views": row.views,
            }
            for row in result
        ]


