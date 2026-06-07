from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import require_roles
from app.database.session import get_db
from app.models.auth.user import User
from app.schemas.core_repository import CoreFileOut, CoreMetadataVersionOut, CoreResearchObjectDetailOut, CoreResearchObjectListOut
from app.services.core.core_repository_service import core_repository_service

router = APIRouter()

ALLOWED_CORE_REPOSITORY_ROLES = ("SUPER_ADMIN", "APPROVER", "REVIEWER", "DATA_ENTRY")


@router.get("", response_model=list[CoreResearchObjectListOut])
async def list_core_records(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    _: User = Depends(require_roles(*ALLOWED_CORE_REPOSITORY_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> list[CoreResearchObjectListOut]:
    return await core_repository_service.list_core_records(db, limit=limit, offset=offset)


@router.get("/{research_id}", response_model=CoreResearchObjectDetailOut)
async def get_core_record(
    research_id: UUID,
    _: User = Depends(require_roles(*ALLOWED_CORE_REPOSITORY_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> CoreResearchObjectDetailOut:
    return await core_repository_service.get_core_record(db, research_id=research_id)


@router.get("/{research_id}/files", response_model=list[CoreFileOut])
async def list_core_files(
    research_id: UUID,
    _: User = Depends(require_roles(*ALLOWED_CORE_REPOSITORY_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> list[CoreFileOut]:
    return await core_repository_service.list_core_files(db, research_id=research_id)


@router.get("/{research_id}/versions", response_model=list[CoreMetadataVersionOut])
async def list_core_metadata_versions(
    research_id: UUID,
    _: User = Depends(require_roles(*ALLOWED_CORE_REPOSITORY_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> list[CoreMetadataVersionOut]:
    return await core_repository_service.list_metadata_versions(db, research_id=research_id)
