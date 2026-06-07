from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

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
