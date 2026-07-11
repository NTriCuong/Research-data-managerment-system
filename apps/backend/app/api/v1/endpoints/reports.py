from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status
from uuid import UUID


from app.core.permissions import require_roles
from app.database.session import get_db
from app.models.auth.user import User
from app.schemas.reports import (
    MetadataQualityOut,
    PendingStatusOut,
    StatusBreakdownItem,
    TopDepartmentItem,
    TotalCoreRepositoriesOut,
    TotalResearchersOut,
)
from app.schemas.logs import (
    CountViewsResponse,
    MonthlyViewResponse,
    ResearchViewResponse,
    TopResearchViewResponse,
    YearlyViewResponse,
)
from app.services.logs.research_view_report_service import (
    ResearchObjectViewService,
)
from app.services.reports.reports_service import report_service

router = APIRouter()

ALLOWED_REPORT_ROLES = ("SUPER_ADMIN", "MANAGER")


@router.get("/total-core-repositories", response_model=TotalCoreRepositoriesOut)
async def total_core_repositories(
    _: User = Depends(require_roles(*ALLOWED_REPORT_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> TotalCoreRepositoriesOut:
    return await report_service.report_total_core_repositories(db)


@router.get("/pending-status", response_model=PendingStatusOut)
async def research_pending_status(
    _: User = Depends(require_roles(*ALLOWED_REPORT_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> PendingStatusOut:
    return await report_service.report_research_spending_status(db)


@router.get("/total-researchers", response_model=TotalResearchersOut)
async def total_researchers(
    _: User = Depends(require_roles(*ALLOWED_REPORT_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> TotalResearchersOut:
    return await report_service.report_total_researches(db)


@router.get("/metadata-quality", response_model=MetadataQualityOut)
async def metadata_quality_score(
    _: User = Depends(require_roles(*ALLOWED_REPORT_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> MetadataQualityOut:
    return await report_service.report_metadata_quality_score(db)


@router.get("/status-breakdown", response_model=list[StatusBreakdownItem])
async def status_breakdown(
    _: User = Depends(require_roles(*ALLOWED_REPORT_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> list[StatusBreakdownItem]:
    return await report_service.report_status_of_research(db)


@router.get("/top-departments", response_model=list[TopDepartmentItem])
async def top_contributing_departments(
    limit: int = Query(default=10, ge=1, le=50),
    _: User = Depends(require_roles(*ALLOWED_REPORT_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> list[TopDepartmentItem]:
    return await report_service.report_top_contributing_department(db, limit=limit)


# Add view
@router.post(
    "/research-views/{research_id}",
    response_model=ResearchViewResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_view(
    research_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> ResearchViewResponse:
    return await ResearchObjectViewService(db).add_view(
        research_id,
    )
# Count views

@router.get(
    "/research-views/{research_id}/count",
    response_model=CountViewsResponse,
)
async def count_views(
    research_id: UUID,
    _: User = Depends(require_roles(*ALLOWED_REPORT_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> CountViewsResponse:
    return await ResearchObjectViewService(db).count_views(
        research_id,
    )

# Monthly statistics

@router.get(
    "/research-views/{research_id}/monthly",
    response_model=list[MonthlyViewResponse],
)
async def count_views_by_month(
    research_id: UUID,
    year: int = Query(..., ge=2000),
    _: User = Depends(require_roles(*ALLOWED_REPORT_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> list[MonthlyViewResponse]:
    return await ResearchObjectViewService(db).count_views_by_month(
        research_id,
        year,
    )

# Yearly statistics

@router.get(
    "/research-views/{research_id}/yearly",
    response_model=list[YearlyViewResponse],
)
async def count_views_by_year(
    research_id: UUID,
    _: User = Depends(require_roles(*ALLOWED_REPORT_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> list[YearlyViewResponse]:
    return await ResearchObjectViewService(db).count_views_by_year(
        research_id,
    )

# Top 10 by month
@router.get(
    "/research-views/top/month",
    response_model=list[TopResearchViewResponse],
)
async def top10_views_by_month(
    year: int = Query(..., ge=2000),
    month: int = Query(..., ge=1, le=12),
    limit: int = Query(10, ge=1, le=100),
    _: User = Depends(require_roles(*ALLOWED_REPORT_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> list[TopResearchViewResponse]:
    return await ResearchObjectViewService(db).top10_views_by_month(
        year,
        month,
        limit,
    )
# Top 10 by year

@router.get(
    "/research-views/top/year",
    response_model=list[TopResearchViewResponse],
)
async def top10_views_by_year(
    year: int = Query(..., ge=2000),
    limit: int = Query(10, ge=1, le=100),
    _: User = Depends(require_roles(*ALLOWED_REPORT_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> list[TopResearchViewResponse]:
    return await ResearchObjectViewService(db).top10_views_by_year(
        year,
        limit,
    )

# Top 10 by domain

@router.get(
    "/research-views/top/domain/{domain_id}",
    response_model=list[TopResearchViewResponse],
)
async def top10_views_by_domain(
    domain_id: UUID,
    year: int = Query(..., ge=2000),
    limit: int = Query(10, ge=1, le=100),
    _: User = Depends(require_roles(*ALLOWED_REPORT_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> list[TopResearchViewResponse]:
    return await ResearchObjectViewService(db).top10_views_by_domain(
        domain_id,
        year,
        limit,
    )