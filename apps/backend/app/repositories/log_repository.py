from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.logs.audit_log import AuditLog
from app.models.logs.login_log import LoginLog
from app.models.logs.workflow_history import WorkflowHistory


class LogRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_audit_logs(
        self,
        *,
        actor_user_id: UUID | None,
        action_code: str | None,
        result: str | None,
        target_table: str | None,
        created_from: datetime | None,
        created_to: datetime | None,
        limit: int,
        offset: int,
    ) -> list[AuditLog]:
        stmt = select(AuditLog).order_by(AuditLog.created_at.desc()).offset(offset).limit(limit)
        if actor_user_id is not None:
            stmt = stmt.where(AuditLog.actor_user_id == actor_user_id)
        if action_code is not None:
            stmt = stmt.where(AuditLog.action_code == action_code)
        if result is not None:
            stmt = stmt.where(AuditLog.result == result)
        if target_table is not None:
            stmt = stmt.where(AuditLog.target_table == target_table)
        if created_from is not None:
            stmt = stmt.where(AuditLog.created_at >= created_from)
        if created_to is not None:
            stmt = stmt.where(AuditLog.created_at <= created_to)
        return list((await self.db.execute(stmt)).scalars().all())

    async def list_login_logs(
        self,
        *,
        user_id: UUID | None,
        username: str | None,
        login_result: str | None,
        created_from: datetime | None,
        created_to: datetime | None,
        limit: int,
        offset: int,
    ) -> list[LoginLog]:
        stmt = select(LoginLog).order_by(LoginLog.created_at.desc()).offset(offset).limit(limit)
        if user_id is not None:
            stmt = stmt.where(LoginLog.user_id == user_id)
        if username is not None:
            stmt = stmt.where(LoginLog.username_attempted.ilike(f"%{username}%"))
        if login_result is not None:
            stmt = stmt.where(LoginLog.login_result == login_result)
        if created_from is not None:
            stmt = stmt.where(LoginLog.created_at >= created_from)
        if created_to is not None:
            stmt = stmt.where(LoginLog.created_at <= created_to)
        return list((await self.db.execute(stmt)).scalars().all())

    async def list_workflow_logs(
        self,
        *,
        staging_id: UUID | None,
        research_id: UUID | None,
        performed_by: UUID | None,
        action_code: str | None,
        performed_from: datetime | None,
        performed_to: datetime | None,
        limit: int,
        offset: int,
    ) -> list[WorkflowHistory]:
        stmt = select(WorkflowHistory).order_by(WorkflowHistory.performed_at.desc()).offset(offset).limit(limit)
        if staging_id is not None:
            stmt = stmt.where(WorkflowHistory.staging_id == staging_id)
        if research_id is not None:
            stmt = stmt.where(WorkflowHistory.research_id == research_id)
        if performed_by is not None:
            stmt = stmt.where(WorkflowHistory.performed_by == performed_by)
        if action_code is not None:
            stmt = stmt.where(WorkflowHistory.action_code == action_code)
        if performed_from is not None:
            stmt = stmt.where(WorkflowHistory.performed_at >= performed_from)
        if performed_to is not None:
            stmt = stmt.where(WorkflowHistory.performed_at <= performed_to)
        return list((await self.db.execute(stmt)).scalars().all())
