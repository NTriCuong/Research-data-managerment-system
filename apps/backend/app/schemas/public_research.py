from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from app.models.enum import AccessLevel, AuthorRole


class PublicLookupOut(BaseModel):
    id: UUID
    name: str


class PublicResearchLookupsOut(BaseModel):
    output_types: list[PublicLookupOut]
    departments: list[PublicLookupOut]
    domains: list[PublicLookupOut]
    keywords: list[PublicLookupOut]


class PublicAuthorOut(BaseModel):
    full_name: str
    email: str | None
    affiliation: str | None
    author_order: int
    author_role: AuthorRole


class PublicFileOut(BaseModel):
    file_id: UUID
    original_filename: str
    mime_type: str
    file_extension: str | None
    file_size_bytes: int
    uploaded_at: datetime
    access_level: AccessLevel


class PublicResearchListItemOut(BaseModel):
    research_id: UUID
    title: str
    description: str | None
    cover_image_url: str | None
    year: int | None
    output_type: PublicLookupOut
    department: PublicLookupOut
    authors: list[PublicAuthorOut]
    domains: list[PublicLookupOut]
    keywords: list[PublicLookupOut]
    access_level: AccessLevel
    version_no: int
    approved_at: datetime
    metadata_quality_score: Decimal | None


class PublicResearchListOut(BaseModel):
    items: list[PublicResearchListItemOut]
    total: int
    limit: int
    offset: int


class PublicResearchDetailOut(PublicResearchListItemOut):
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
    file_attachments: list[PublicFileOut]


class PublicResearchDownloadOut(BaseModel):
    download_url: str
    expires_in: int
