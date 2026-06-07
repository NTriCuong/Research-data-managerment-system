from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.log_repository import LogRepository
from app.schemas.logs import AuditLogOut, LoginLogOut, WorkflowLogOut


class LogQueryService:
    async def list_audit_logs(
        self,
        db: AsyncSession,
        *,
        actor_user_id: UUID | None,
        action_code: str | None,
        result: str | None,
        target_table: str | None,
        created_from: datetime | None,
        created_to: datetime | None,
        limit: int,
        offset: int,
    ) -> list[AuditLogOut]:
        rows = await LogRepository(db).list_audit_logs(
            actor_user_id=actor_user_id,
            action_code=action_code,
            result=result,
            target_table=target_table,
            created_from=created_from,
            created_to=created_to,
            limit=limit,
            offset=offset,
        )
        return [AuditLogOut.model_validate(row) for row in rows]

    async def list_login_logs(
        self,
        db: AsyncSession,
        *,
        user_id: UUID | None,
        username: str | None,
        login_result: str | None,
        created_from: datetime | None,
        created_to: datetime | None,
        limit: int,
        offset: int,
    ) -> list[LoginLogOut]:
        rows = await LogRepository(db).list_login_logs(
            user_id=user_id,
            username=username,
            login_result=login_result,
            created_from=created_from,
            created_to=created_to,
            limit=limit,
            offset=offset,
        )
        return [LoginLogOut.model_validate(row) for row in rows]

    async def list_workflow_logs(
        self,
        db: AsyncSession,
        *,
        staging_id: UUID | None,
        research_id: UUID | None,
        performed_by: UUID | None,
        action_code: str | None,
        performed_from: datetime | None,
        performed_to: datetime | None,
        limit: int,
        offset: int,
    ) -> list[WorkflowLogOut]:
        rows = await LogRepository(db).list_workflow_logs(
            staging_id=staging_id,
            research_id=research_id,
            performed_by=performed_by,
            action_code=action_code,
            performed_from=performed_from,
            performed_to=performed_to,
            limit=limit,
            offset=offset,
        )
        return [WorkflowLogOut.model_validate(row) for row in rows]


log_query_service = LogQueryService()
