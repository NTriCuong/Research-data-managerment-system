import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.reference.user_device import UserDevice
from app.models.auth.user import User
from app.schemas.notification import RegisterTokenRequest
from app.core.permissions import get_current_user

from app.services.notification.notification_service import notification_service

router = APIRouter()


# GET NOTIFICATIONS (chỉ trả thông báo của user hiện tại)
@router.get("/")
async def get_notifications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await notification_service.get_notifications(db, current_user.user_id)


# MARK AS READ
@router.patch("/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await notification_service.mark_as_read(db, notification_id, current_user.user_id)
    return {"message": "Đã đánh dấu đã đọc"}


# REGISTER FCM TOKEN
@router.post("/register-token")
async def register_token(
    payload: RegisterTokenRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    from sqlalchemy import select
    result = await db.execute(
        select(UserDevice).where(UserDevice.user_id == current_user.user_id)
    )
    existing = result.scalar_one_or_none()
    if existing:
        existing.fcm_token = payload.fcm_token
        existing.device_name = payload.device_name
        await db.commit()
        await db.refresh(existing)
        return {"message": "Token updated"}

    new_device = UserDevice(
        user_id=current_user.user_id,
        fcm_token=payload.fcm_token,
        device_name=payload.device_name
    )
    db.add(new_device)
    await db.commit()
    await db.refresh(new_device)
    return {"message": "Token registered"}
