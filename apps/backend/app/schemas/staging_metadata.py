from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.enum import AccessLevel, AuthorRole, WorkflowStatus


class StagingAuthorIn(BaseModel):
    researcher_id: UUID | None = None
    full_name: str
    email: str | None = None
    affiliation: str | None = None
    author_order: int = 1
    author_role: AuthorRole = AuthorRole.creator


class StagingAuthorOut(StagingAuthorIn):
    model_config = ConfigDict(from_attributes=True)

    staging_author_id: UUID
    staging_id: UUID
    created_at: datetime


class StagingResearchObjectCreate(BaseModel):
    title: str
    output_type_id: UUID
    department_id: UUID
    year: int | None = None
    description: str | None = None
    abstract: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    date_issued: date | None = None
    publisher: str | None = None
    language: str | None = "vi"
    identifier: str | None = None
    external_url: str | None = None
    source: str | None = None
    relation: str | None = None
    coverage: str | None = None
    rights: str | None = None
    access_level: AccessLevel = AccessLevel.internal
    domain_ids: list[UUID] = []
    keyword_ids: list[UUID] = []
    authors: list[StagingAuthorIn] = []


class StagingResearchObjectUpdate(BaseModel):
    title: str | None = None
    output_type_id: UUID | None = None
    department_id: UUID | None = None
    year: int | None = None
    description: str | None = None
    abstract: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    date_issued: date | None = None
    publisher: str | None = None
    language: str | None = None
    identifier: str | None = None
    external_url: str | None = None
    source: str | None = None
    relation: str | None = None
    coverage: str | None = None
    rights: str | None = None
    access_level: AccessLevel | None = None
    domain_ids: list[UUID] | None = None
    keyword_ids: list[UUID] | None = None
    authors: list[StagingAuthorIn] | None = None


class StagingResearchObjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    staging_id: UUID
    title: str
    output_type_id: UUID
    department_id: UUID
    year: int | None
    workflow_status: WorkflowStatus
    access_level: AccessLevel
    source_core_research_id: UUID | None
    update_reason: str | None
    metadata_quality_score: Decimal | None
    created_by: UUID
    submitted_by: UUID | None
    submitted_at: datetime | None
    created_at: datetime
    updated_at: datetime | None


class SubmitForReviewRequest(BaseModel):
    note: str | None = None


class CreateRevisionRequest(BaseModel):
    research_id: UUID
    update_reason: str


class StagingFileCreate(BaseModel):
    original_filename: str
    stored_filename: str
    storage_path: str
    mime_type: str
    file_extension: str | None = None
    file_size_bytes: int
    checksum_sha256: str | None = None
    access_level: AccessLevel = AccessLevel.internal


class StagingFileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    file_id: UUID
    staging_id: UUID
    original_filename: str
    stored_filename: str
    storage_path: str
    mime_type: str
    file_extension: str | None
    file_size_bytes: int
    checksum_sha256: str | None
    uploaded_by: UUID
    uploaded_at: datetime
    access_level: AccessLevel
