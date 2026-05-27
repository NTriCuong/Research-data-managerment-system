from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enum import WorkflowStatus
from app.models.logs.workflow_history import WorkflowHistory


class WorkflowService:
    async def write_history(
        self,
        db: AsyncSession,
        *,
        staging_id: UUID | None = None,
        research_id: UUID | None = None,
        performed_by: UUID,
        from_status: WorkflowStatus | None,
        to_status: WorkflowStatus,
        action_code: str,
        action_note: str | None = None,
    ) -> None:
        if staging_id is None and research_id is None:
            raise ValueError("workflow_history requires staging_id or research_id")
        db.add(
            WorkflowHistory(
                staging_id=staging_id,
                research_id=research_id,
                from_status=from_status,
                to_status=to_status,
                action_code=action_code,
                action_note=action_note,
                performed_by=performed_by,
            )
        )
        await db.flush()


workflow_service = WorkflowService()
