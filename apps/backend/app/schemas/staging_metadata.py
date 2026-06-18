from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl, model_validator

from app.models.enum import AccessLevel, AuthorRole, FileStatus, WorkflowStatus


class StagingAuthorIn(BaseModel):
    researcher_id: UUID | None = None
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    email: EmailStr | None = None
    affiliation: str | None = Field(default=None, max_length=255)
    author_order: int = Field(default=1, ge=1)
    author_role: AuthorRole = AuthorRole.creator

    @model_validator(mode="after")
    def require_identifier_or_name(self) -> "StagingAuthorIn":
        if self.researcher_id is None and not self.full_name:
            raise ValueError("author requires researcher_id or full_name")
        return self


class StagingAuthorOut(StagingAuthorIn):
    model_config = ConfigDict(from_attributes=True)

    staging_author_id: UUID
    staging_id: UUID
    created_at: datetime


class StagingResearchObjectCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    output_type_id: UUID
    department_id: UUID
    year: int | None = Field(default=None, ge=1900, le=2100)
    description: str | None = None
    abstract: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    date_issued: date | None = None
    publisher: str | None = Field(default=None, max_length=255)
    language: str | None = Field(default="vi", min_length=2, max_length=10)
    identifier: str | None = Field(default=None, max_length=255)
    external_url: HttpUrl | None = None
    source: str | None = None
    relation: str | None = None
    coverage: str | None = None
    rights: str | None = None
    domain_ids: list[UUID] = Field(default_factory=list)
    keyword_ids: list[UUID] = Field(default_factory=list)
    domain_name: list[str] = Field(default_factory=list)
    keyword_name: list[str] = Field(default_factory=list)
    authors: list[StagingAuthorIn] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def reject_name_based_references(cls, data):
        if isinstance(data, dict):
            unsupported = {"domain_name", "keyword_name"} & set(data)
            if unsupported:
                fields = ", ".join(sorted(unsupported))
                raise ValueError(f"{fields} không được hỗ trợ; hãy dùng domain_ids/keyword_ids đã tồn tại")
        return data


class StagingResearchObjectUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=500)
    output_type_id: UUID | None = None
    department_id: UUID | None = None
    year: int | None = Field(default=None, ge=1900, le=2100)
    description: str | None = None
    abstract: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    date_issued: date | None = None
    publisher: str | None = Field(default=None, max_length=255)
    language: str | None = Field(default=None, min_length=2, max_length=10)
    identifier: str | None = Field(default=None, max_length=255)
    external_url: HttpUrl | None = None
    source: str | None = None
    relation: str | None = None
    coverage: str | None = None
    rights: str | None = None
    domain_ids: list[UUID] | None = None
    keyword_ids: list[UUID] | None = None
    domain_name: list[str] | None = None
    keyword_name: list[str] | None = None
    authors: list[StagingAuthorIn] | None = None

    @model_validator(mode="before")
    @classmethod
    def reject_name_based_references(cls, data):
        if isinstance(data, dict):
            unsupported = {"domain_name", "keyword_name"} & set(data)
            if unsupported:
                fields = ", ".join(sorted(unsupported))
                raise ValueError(f"{fields} không được hỗ trợ; hãy dùng domain_ids/keyword_ids đã tồn tại")
        return data


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
    note: str | None = Field(default=None, max_length=1000)


class BulkSubmitForReviewRequest(BaseModel):
    staging_ids: list[UUID] = Field(min_length=1, max_length=100)
    note: str | None = Field(default=None, max_length=1000)


class BulkSubmitForReviewItemOut(BaseModel):
    staging_id: UUID
    success: bool
    message: str


class BulkSubmitForReviewOut(BaseModel):
    submitted_count: int
    failed_count: int
    results: list[BulkSubmitForReviewItemOut]


class CreateRevisionRequest(BaseModel):
    research_id: UUID
    update_reason: str = Field(min_length=1, max_length=1000)


class StagingFileCreate(BaseModel):
    original_filename: str = Field(min_length=1, max_length=255)
    stored_filename: str = Field(min_length=1, max_length=255)
    storage_path: str = Field(min_length=1, max_length=1000)
    mime_type: str = Field(min_length=1, max_length=255)
    file_extension: str | None = Field(default=None, max_length=20)
    file_size_bytes: int = Field(gt=0)
    checksum_sha256: str | None = Field(default=None, min_length=64, max_length=64)


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
    file_status: FileStatus
    uploaded_by: UUID
    uploaded_at: datetime
    access_level: AccessLevel


class WorkflowHistoryOut(BaseModel):
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
