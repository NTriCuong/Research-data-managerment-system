from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.database.session import get_db
from app.models.auth.user import User
from app.schemas.notification import NotificationOut
from app.services.auth.deps import get_current_active_user
from app.services.notifications.notification_service import notification_service

router = APIRouter()


@router.get("", response_model=list[NotificationOut])
async def list_my_notifications(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    unread_only: bool = Query(default=False),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> list[NotificationOut]:
    return await notification_service.list_my_notifications(
        db,
        current_user=current_user,
        limit=limit,
        offset=offset,
        unread_only=unread_only,
    )


@router.post("/{notification_id}/read", response_model=NotificationOut)
async def mark_notification_read(
    notification_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> NotificationOut:
    notification = await notification_service.mark_read(
        db,
        notification_id=notification_id,
        current_user=current_user,
    )
    if notification is None:
        raise NotFoundException("Khong tim thay thong bao")
    return notification
