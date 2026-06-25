from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import require_roles
from app.database.session import get_db
from app.models.auth.user import User
from app.models.enum import WorkflowStatus
from app.schemas.search import CoreSearchResponseOut, StagingSearchResponseOut
from app.services.auth.deps import get_optional_current_active_user
from app.services.search.search_service import search_service

router = APIRouter()

ALLOWED_STAGING_SEARCH_ROLES = ("SUPER_ADMIN", "MANAGER", "DATA_ENTRY", "REVIEWER", "APPROVER")


@router.get("/core", response_model=CoreSearchResponseOut)
async def search_core_postgres(
    q: str = Query(min_length=1, max_length=300),
    output_type_id: list[UUID] | None = Query(default=None),
    department_id: list[UUID] | None = Query(default=None),
    domain_id: list[UUID] | None = Query(default=None),
    keyword_id: list[UUID] | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User | None = Depends(get_optional_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> CoreSearchResponseOut:
    return await search_service.search_core_postgres(
        db,
        query=q.strip(),
        output_type_ids=output_type_id,
        department_ids=department_id,
        domain_ids=domain_id,
        keyword_ids=keyword_id,
        limit=limit,
        offset=offset,
        current_user=current_user,
    )


@router.get("/staging", response_model=StagingSearchResponseOut)
async def search_staging_postgres(
    q: str = Query(min_length=1, max_length=300),
    workflow_status: list[WorkflowStatus] | None = Query(default=None),
    output_type_id: list[UUID] | None = Query(default=None),
    department_id: list[UUID] | None = Query(default=None),
    domain_id: list[UUID] | None = Query(default=None),
    keyword_id: list[UUID] | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(require_roles(*ALLOWED_STAGING_SEARCH_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> StagingSearchResponseOut:
    return await search_service.search_staging_postgres(
        db,
        query=q.strip(),
        workflow_statuses=workflow_status,
        output_type_ids=output_type_id,
        department_ids=department_id,
        domain_ids=domain_id,
        keyword_ids=keyword_id,
        limit=limit,
        offset=offset,
        current_user=current_user,
    )
