from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.auth.user import User
from app.schemas.core_approve import CoreSearchResponseOut
from app.services.auth.deps import get_optional_current_active_user
from app.services.search.search_service import search_service

router = APIRouter()


@router.get("/core", response_model=CoreSearchResponseOut)
async def search_core_postgres(
    q: str = Query(min_length=1, max_length=300),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User | None = Depends(get_optional_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> CoreSearchResponseOut:
    return await search_service.search_core_postgres(
        db,
        query=q.strip(),
        limit=limit,
        offset=offset,
        current_user=current_user,
    )
