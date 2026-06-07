from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import require_roles
from app.database.session import get_db
from app.models.auth.user import User
from app.schemas.logs import AuditLogOut, LoginLogOut, WorkflowLogOut
from app.services.logs.log_query_service import log_query_service


router = APIRouter()


@router.get("/audit", response_model=list[AuditLogOut])
async def list_audit_logs(
    actor_user_id: UUID | None = Query(default=None),
    action_code: str | None = Query(default=None, max_length=100),
    result: str | None = Query(default=None, max_length=50),
    target_table: str | None = Query(default=None, max_length=100),
    created_from: datetime | None = Query(default=None),
    created_to: datetime | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    _: User = Depends(require_roles("SUPER_ADMIN")),
    db: AsyncSession = Depends(get_db),
) -> list[AuditLogOut]:
    return await log_query_service.list_audit_logs(
        db,
        actor_user_id=actor_user_id,
        action_code=action_code,
        result=result,
        target_table=target_table,
        created_from=created_from,
        created_to=created_to,
        limit=limit,
        offset=offset,
    )


@router.get("/login", response_model=list[LoginLogOut])
async def list_login_logs(
    user_id: UUID | None = Query(default=None),
    username: str | None = Query(default=None, max_length=255),
    login_result: str | None = Query(default=None, max_length=50),
    created_from: datetime | None = Query(default=None),
    created_to: datetime | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    _: User = Depends(require_roles("SUPER_ADMIN")),
    db: AsyncSession = Depends(get_db),
) -> list[LoginLogOut]:
    return await log_query_service.list_login_logs(
        db,
        user_id=user_id,
        username=username,
        login_result=login_result,
        created_from=created_from,
        created_to=created_to,
        limit=limit,
        offset=offset,
    )


@router.get("/workflow", response_model=list[WorkflowLogOut])
async def list_workflow_logs(
    staging_id: UUID | None = Query(default=None),
    research_id: UUID | None = Query(default=None),
    performed_by: UUID | None = Query(default=None),
    action_code: str | None = Query(default=None, max_length=100),
    performed_from: datetime | None = Query(default=None),
    performed_to: datetime | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    _: User = Depends(require_roles("SUPER_ADMIN", "MANAGER")),
    db: AsyncSession = Depends(get_db),
) -> list[WorkflowLogOut]:
    return await log_query_service.list_workflow_logs(
        db,
        staging_id=staging_id,
        research_id=research_id,
        performed_by=performed_by,
        action_code=action_code,
        performed_from=performed_from,
        performed_to=performed_to,
        limit=limit,
        offset=offset,
    )
