from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enum import WorkflowStatus
from app.repositories.reports_repository import ReportsRepository
from app.schemas.reports import (
    MetadataQualityOut,
    PendingStatusOut,
    StatusBreakdownItem,
    TopDepartmentItem,
    TotalCoreRepositoriesOut,
    TotalResearchersOut,
)


class ReportService:

    # ── 1. Tổng số bài nghiên cứu trong core DB ───────────────────────────────

    async def report_total_core_repositories(self, db: AsyncSession) -> TotalCoreRepositoriesOut:
        repo = ReportsRepository(db)
        total = await repo.count_core_repositories()
        return TotalCoreRepositoriesOut(total_core_repositories=total)

    # ── 2. Tổng số bài đang chờ duyệt trong staging ───────────────────────────

    async def report_research_spending_status(self, db: AsyncSession) -> PendingStatusOut:
        repo = ReportsRepository(db)
        count_review = await repo.count_staging_by_status(WorkflowStatus.pending_review)
        count_approval = await repo.count_staging_by_status(WorkflowStatus.pending_approval)
        return PendingStatusOut(
            pending_review=count_review,
            pending_approval=count_approval,
            total_pending=count_review + count_approval,
        )

    # ── 3. Tổng số nhà nghiên cứu trong hệ thống ─────────────────────────────

    async def report_total_researches(self, db: AsyncSession) -> TotalResearchersOut:
        repo = ReportsRepository(db)
        return TotalResearchersOut(
            total_researchers=await repo.count_researchers(),
            internal=await repo.count_researchers_by_internal(True),
            external=await repo.count_researchers_by_internal(False),
        )

    # ── 4. Điểm chất lượng metadata ───────────────────────────────────────────

    async def report_metadata_quality_score(self, db: AsyncSession) -> MetadataQualityOut:
        repo = ReportsRepository(db)
        stats = await repo.get_metadata_quality_stats()
        return MetadataQualityOut(
            avg_score=round(stats["avg_score"], 2),
            min_score=stats["min_score"],
            max_score=stats["max_score"],
            total_records=stats["total_records"],
        )

    # ── 5. Báo cáo theo trạng thái bài nghiên cứu (staging) ──────────────────

    async def report_status_of_research(self, db: AsyncSession) -> list[StatusBreakdownItem]:
        repo = ReportsRepository(db)
        rows = await repo.count_staging_group_by_status()
        return [StatusBreakdownItem(status=r["status"], count=r["count"]) for r in rows]

    # ── 6. Báo cáo khoa đóng góp nhiều nhất ──────────────────────────────────

    async def report_top_contributing_department(
        self, db: AsyncSession, *, limit: int = 10
    ) -> list[TopDepartmentItem]:
        repo = ReportsRepository(db)
        rows = await repo.top_contributing_departments(limit=limit)
        return [TopDepartmentItem(department_name=r["department_name"], count=r["count"]) for r in rows]


report_service = ReportService()
