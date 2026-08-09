from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enum import AccessLevel, WorkflowStatus
from app.schemas.search import CoreSearchResponseOut, CoreSearchResultOut


class RejectApprovalRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=1000)


class ApproveRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    note: str | None = Field(default=None, max_length=1000)


class PendingApprovalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    staging_id: UUID
    title: str
    output_type_id: UUID
    department_id: UUID
    year: int | None
    workflow_status: WorkflowStatus
    access_level: AccessLevel
    metadata_quality_score: Decimal | None
    submitted_by: UUID | None
    reviewed_by: UUID | None
    submitted_at: datetime | None
    reviewed_at: datetime | None
    created_at: datetime
    updated_at: datetime | None
