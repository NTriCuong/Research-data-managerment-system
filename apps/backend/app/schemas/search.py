from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.enum import AccessLevel, WorkflowStatus


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


class StagingSearchResultOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    staging_id: UUID
    title: str
    output_type_id: UUID
    department_id: UUID
    year: int | None
    workflow_status: WorkflowStatus
    access_level: AccessLevel
    source_core_research_id: UUID | None
    created_by: UUID
    created_at: datetime
    updated_at: datetime | None
    rank: float


class StagingSearchResponseOut(BaseModel):
    items: list[StagingSearchResultOut]
    total: int
    limit: int
    offset: int
