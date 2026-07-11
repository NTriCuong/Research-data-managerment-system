import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.research_object_view_repository import (
    ResearchObjectViewRepository,
)
from app.schemas.logs import (
    CountViewsResponse,
    MonthlyViewResponse,
    ResearchViewResponse,
    TopResearchViewResponse,
    YearlyViewResponse,
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
# đếm lượt xem research_id
    async def count_views(
        self,
        research_id: uuid.UUID,
    ) -> CountViewsResponse:
        """
        Tổng số lượt xem của một research
        """
        total_views = await self.repository.count_views(research_id)

        return CountViewsResponse(
            research_id=research_id,
            total_views=total_views,
        )
# lượt xem theo tháng
    async def count_views_by_month(
        self,
        research_id: uuid.UUID,
        year: int,
    ) -> list[MonthlyViewResponse]:
        """
        Thống kê lượt xem theo từng tháng trong năm
        """
        result = await self.repository.count_views_by_month(
            research_id=research_id,
            year=year,
        )

        return [
            MonthlyViewResponse(**item)
            for item in result
        ]
#        Thống kê lượt xem theo từng năm
    async def count_views_by_year(
        self,
        research_id: uuid.UUID,
    ) -> list[YearlyViewResponse]:
        """
        Thống kê lượt xem theo từng năm
        """
        result = await self.repository.count_views_by_year(
            research_id=research_id,
        )

        return [
            YearlyViewResponse(**item)
            for item in result
        ]

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