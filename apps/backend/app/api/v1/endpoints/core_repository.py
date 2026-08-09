from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import require_roles
from app.database.session import get_db
from app.models.auth.user import User
from app.schemas.core_repository import (
    CoreFileAccessLevelUpdate,
    CoreFileOut,
    CoreMetadataVersionOut,
    CoreResearchAccessLevelUpdate,
    CoreResearchObjectDetailOut,
    CoreResearchObjectListOut,
)
from app.services.core.core_repository_service import core_repository_service

router = APIRouter()

ALLOWED_CORE_REPOSITORY_ROLES = ("SUPER_ADMIN", "APPROVER", "REVIEWER", "DATA_ENTRY")
ALLOWED_FILE_PERMISSION_MANAGER_ROLES = ("SUPER_ADMIN", "APPROVER")


@router.get("", response_model=list[CoreResearchObjectListOut])
async def list_core_records(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    _: User = Depends(require_roles(*ALLOWED_CORE_REPOSITORY_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> list[CoreResearchObjectListOut]:
    return await core_repository_service.list_core_records(db, limit=limit, offset=offset)


@router.get("/mine", response_model=list[CoreResearchObjectListOut])
async def list_my_core_records(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(require_roles("SUPER_ADMIN", "DATA_ENTRY")),
    db: AsyncSession = Depends(get_db),
) -> list[CoreResearchObjectListOut]:
    return await core_repository_service.list_my_core_records(
        db,
        creator_id=current_user.user_id,
        limit=limit,
        offset=offset,
    )

@router.get("/{research_id}", response_model=CoreResearchObjectDetailOut)
async def get_core_record(
    research_id: UUID,
    _: User = Depends(require_roles(*ALLOWED_CORE_REPOSITORY_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> CoreResearchObjectDetailOut:
    return await core_repository_service.get_core_record(db, research_id=research_id)


@router.patch("/{research_id}/access-level", response_model=CoreResearchObjectListOut)
async def update_core_research_access_level(
    research_id: UUID,
    payload: CoreResearchAccessLevelUpdate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_roles(*ALLOWED_FILE_PERMISSION_MANAGER_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> CoreResearchObjectListOut:
    return await core_repository_service.update_core_research_access_level(
        db,
        research_id=research_id,
        access_level=payload.access_level,
        background_tasks=background_tasks,
        current_user=current_user,
    )


@router.get("/{research_id}/files", response_model=list[CoreFileOut])
async def list_core_files(
    research_id: UUID,
    _: User = Depends(require_roles(*ALLOWED_CORE_REPOSITORY_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> list[CoreFileOut]:
    return await core_repository_service.list_core_files(db, research_id=research_id)


@router.patch("/{research_id}/files/{file_id}/access-level", response_model=CoreFileOut)
async def update_core_file_access_level(
    research_id: UUID,
    file_id: UUID,
    payload: CoreFileAccessLevelUpdate,
    current_user: User = Depends(require_roles(*ALLOWED_FILE_PERMISSION_MANAGER_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> CoreFileOut:
    return await core_repository_service.update_core_file_access_level(
        db,
        research_id=research_id,
        file_id=file_id,
        access_level=payload.access_level,
        current_user=current_user,
    )


@router.get("/{research_id}/versions", response_model=list[CoreMetadataVersionOut])
async def list_core_metadata_versions(
    research_id: UUID,
    _: User = Depends(require_roles(*ALLOWED_CORE_REPOSITORY_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> list[CoreMetadataVersionOut]:
    return await core_repository_service.list_metadata_versions(db, research_id=research_id)
