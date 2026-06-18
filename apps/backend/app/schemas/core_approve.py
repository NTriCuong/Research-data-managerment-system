from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enum import AccessLevel, WorkflowStatus


class RejectApprovalRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=1000)


class FileAccessLevelAssignment(BaseModel):
    file_id: UUID
    access_level: AccessLevel


class ApproveRequest(BaseModel):
    note: str | None = Field(default=None, max_length=1000)
    access_level: AccessLevel
    file_access_levels: list[FileAccessLevelAssignment] = Field(default_factory=list)


class CoreSearchResultOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    research_id: UUID
    title: str
    year: int | None
    access_level: AccessLevel
    version_no: int
    approved_at: datetime
    rank: float


class CoreSearchResponseOut(BaseModel):
    items: list[CoreSearchResultOut]
    total: int
    limit: int
    offset: int


class PendingApprovalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    staging_id: UUID
    title: str
    output_type_id: UUID
    department_id: UUID
    year: int | None
    workflow_status: WorkflowStatus
    submitted_by: UUID | None
    reviewed_by: UUID | None
    submitted_at: datetime | None
    reviewed_at: datetime | None
    created_at: datetime
    updated_at: datetime | None
