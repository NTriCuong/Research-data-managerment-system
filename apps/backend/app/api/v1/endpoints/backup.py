from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import require_roles
from app.database.session import get_db
from app.models.auth.user import User
from app.schemas.backup import BackupOut
from app.services.backup.backup_service import backup_service


router = APIRouter()


@router.post("/backups", response_model=BackupOut, status_code=status.HTTP_201_CREATED)
async def create_database_backup(
    current_user: User = Depends(require_roles("SUPER_ADMIN")),
    db: AsyncSession = Depends(get_db),
) -> BackupOut:
    return await backup_service.create_database_backup(
        db,
        actor_user_id=current_user.user_id,
    )
