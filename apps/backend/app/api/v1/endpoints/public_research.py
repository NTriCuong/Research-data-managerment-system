from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.auth.user import User
from app.schemas.public_research import (
    PublicResearchDetailOut,
    PublicResearchDownloadOut,
    PublicResearchListOut,
    PublicResearchLookupsOut,
    PublicResearchSuggestionOut,
)
from app.services.auth.deps import get_current_active_user
from app.services.core.public_research_service import public_research_service

router = APIRouter()


@router.get("/research-lookups", response_model=PublicResearchLookupsOut)
async def get_public_research_lookups(
    db: AsyncSession = Depends(get_db),
) -> PublicResearchLookupsOut:
    return await public_research_service.get_public_lookups(db)


@router.get("/researches", response_model=PublicResearchListOut)
async def list_public_researches(
    q: str | None = Query(default=None, min_length=1, max_length=300),
    output_type_ids: list[UUID] | None = Query(default=None),
    department_ids: list[UUID] | None = Query(default=None),
    domain_ids: list[UUID] | None = Query(default=None),
    keyword_ids: list[UUID] | None = Query(default=None),
    author_ids: list[UUID] | None = Query(default=None),
    output_type_id: UUID | None = Query(default=None),
    department_id: UUID | None = Query(default=None),
    domain_id: UUID | None = Query(default=None),
    keyword_id: UUID | None = Query(default=None),
    year: int | None = Query(default=None, ge=1900, le=2100),
    year_from: int | None = Query(default=None, ge=1900, le=2100),
    year_to: int | None = Query(default=None, ge=1900, le=2100),
    has_files: bool = Query(default=False),
    sort: Literal[
        "relevance",
        "newest",
        "oldest",
        "most_viewed",
        "most_downloaded",
        "title_asc",
    ] = Query(default="relevance"),
    limit: int = Query(default=12, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> PublicResearchListOut:
    if year_from is not None and year_to is not None and year_from > year_to:
        year_from, year_to = year_to, year_from

    def merge_ids(values: list[UUID] | None, legacy_value: UUID | None) -> list[UUID] | None:
        merged = list(dict.fromkeys([*(values or []), *([legacy_value] if legacy_value else [])]))
        return merged or None

    return await public_research_service.list_public_researches(
        db,
        q=q.strip() if q else None,
        output_type_ids=merge_ids(output_type_ids, output_type_id),
        department_ids=merge_ids(department_ids, department_id),
        domain_ids=merge_ids(domain_ids, domain_id),
        keyword_ids=merge_ids(keyword_ids, keyword_id),
        author_ids=author_ids,
        year_from=year if year is not None else year_from,
        year_to=year if year is not None else year_to,
        has_files=has_files,
        sort=sort,
        limit=limit,
        offset=offset,
    )


@router.get("/researches/suggestions", response_model=list[PublicResearchSuggestionOut])
async def suggest_public_researches(
    q: str = Query(min_length=2, max_length=100),
    limit: int = Query(default=8, ge=1, le=10),
    db: AsyncSession = Depends(get_db),
) -> list[PublicResearchSuggestionOut]:
    return await public_research_service.suggest_public_researches(
        db,
        q=q.strip(),
        limit=limit,
    )


@router.get("/researches/{research_id}", response_model=PublicResearchDetailOut)
async def get_public_research_detail(
    research_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> PublicResearchDetailOut:
    return await public_research_service.get_public_research_detail(db, research_id=research_id)


@router.post("/researches/{research_id}/files/{file_id}/download", response_model=PublicResearchDownloadOut)
async def create_public_research_file_download(
    research_id: UUID,
    file_id: UUID,
    _: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> PublicResearchDownloadOut:
    return await public_research_service.create_download_url(db, research_id=research_id, file_id=file_id)
