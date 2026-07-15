import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.research_object_view_repository import (
    ResearchObjectViewRepository,
)
from app.schemas.logs import (
    ResearchViewResponse,
    TopResearchViewResponse,
    TotalViewsByYearResponse
)


class ResearchObjectViewService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = ResearchObjectViewRepository(session)
# thêm lượt xem
    async def add_view(
        self,
        research_id: uuid.UUID,
    ) -> ResearchViewResponse:
        """
        Thêm một lượt xem cho research
        """
        view = await self.repository.add_view(research_id)

        await self.session.commit()
        await self.session.refresh(view)

        return ResearchViewResponse.model_validate(view)

    async def top10_views_by_month(
        self,
        year: int,
        month: int,
        limit: int = 10,
    ) -> list[TopResearchViewResponse]:
        """
        Top research có nhiều lượt xem nhất trong tháng
        """
        result = await self.repository.top10_views_by_month(
            year=year,
            month=month,
            limit=limit,
        )

        return [
            TopResearchViewResponse(**item)
            for item in result
        ]

    async def top10_views_by_year(
        self,
        year: int,
        limit: int = 10,
    ) -> list[TopResearchViewResponse]:
        """
        Top research có nhiều lượt xem nhất trong năm
        """
        result = await self.repository.top10_views_by_year(
            year=year,
            limit=limit,
        )

        return [
            TopResearchViewResponse(**item)
            for item in result
        ]

    async def top10_views_by_domain(
        self,
        domain_id: uuid.UUID,
        year: int,
        limit: int = 10,
    ) -> list[TopResearchViewResponse]:
        """
        Top research có nhiều lượt xem nhất theo lĩnh vực
        """
        result = await self.repository.top10_views_by_domain(
            domain_id=domain_id,
            year=year,
            limit=limit,
        )

        return [
            TopResearchViewResponse(**item)
            for item in result
        ]
    async def total_views_by_year(self, year: int) -> list[TotalViewsByYearResponse]:
        result = await self.repository.total_views_by_year(year)
        return [
            TotalViewsByYearResponse(**item)
            for item in result
        ]


