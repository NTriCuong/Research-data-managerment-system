from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.enum import AccessLevel, AuthorRole, FileStatus


class CoreAuthorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    core_author_id: UUID
    research_id: UUID
    researcher_id: UUID | None
    full_name: str
    email: str | None
    affiliation: str | None
    author_order: int
    author_role: AuthorRole
    created_at: datetime


class CoreFileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    file_id: UUID
    research_id: UUID
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


class CoreMetadataVersionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    version_id: UUID
    research_id: UUID
    version_no: int
    metadata_snapshot: dict
    change_reason: str | None
    created_by: UUID
    created_at: datetime


class CoreResearchObjectListOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    research_id: UUID
    title: str
    output_type_id: UUID
    department_id: UUID
    year: int | None
    access_level: AccessLevel
    metadata_quality_score: Decimal | None
    version_no: int
    is_current: bool
    approved_by: UUID
    approved_at: datetime
    created_at: datetime
    updated_at: datetime | None


class CoreResearchObjectDetailOut(CoreResearchObjectListOut):
    source_staging_id: UUID | None
    description: str | None
    abstract: str | None
    start_date: date | None
    end_date: date | None
    date_issued: date | None
    publisher: str | None
    language: str | None
    identifier: str | None
    external_url: str | None
    source: str | None
    relation: str | None
    coverage: str | None
    rights: str | None
    metadata_quality_detail: dict | None
    domain_ids: list[UUID]
    keyword_ids: list[UUID]
    authors: list[CoreAuthorOut]
    file_attachments: list[CoreFileOut]
