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
    output_type_id: UUID | None = Query(default=None),
    department_id: UUID | None = Query(default=None),
    domain_id: UUID | None = Query(default=None),
    keyword_id: UUID | None = Query(default=None),
    year: int | None = Query(default=None, ge=1900, le=2100),
    limit: int = Query(default=12, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> PublicResearchListOut:
    return await public_research_service.list_public_researches(
        db,
        q=q.strip() if q else None,
        output_type_id=output_type_id,
        department_id=department_id,
        domain_id=domain_id,
        keyword_id=keyword_id,
        year=year,
        limit=limit,
        offset=offset,
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
