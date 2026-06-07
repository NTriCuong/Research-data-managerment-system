from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, IPvAnyAddress

from app.models.enum import WorkflowStatus


class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    audit_id: UUID
    actor_user_id: UUID | None
    action_code: str
    target_schema: str | None
    target_table: str | None
    target_id: UUID | None
    old_value: dict[str, Any] | None
    new_value: dict[str, Any] | None
    result: str
    message: str | None
    ip_address: IPvAnyAddress | None
    user_agent: str | None
    created_at: datetime


class LoginLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    login_log_id: UUID
    user_id: UUID | None
    username_attempted: str | None
    login_result: str
    failure_reason: str | None
    ip_address: IPvAnyAddress | None
    user_agent: str | None
    created_at: datetime


class WorkflowLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    workflow_id: UUID
    staging_id: UUID | None
    research_id: UUID | None
    from_status: WorkflowStatus | None
    to_status: WorkflowStatus
    action_code: str
    action_note: str | None
    performed_by: UUID
    performed_at: datetime
    ip_address: IPvAnyAddress | None
    user_agent: str | None
