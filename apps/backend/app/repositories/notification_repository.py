import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reference.notification import Notification
from app.models.reference.user_notification import UserNotification
from app.models.reference.user_device import UserDevice


class NotificationRepository:

    async def create(
        self,
        db: AsyncSession,
        notification: Notification,
    ) -> Notification:
        db.add(notification)
        await db.flush()
        await db.refresh(notification)
        return notification

    async def get_by_user(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
    ) -> list:
        result = await db.execute(
            select(Notification, UserNotification.is_read)
            .join(UserNotification, UserNotification.notification_id == Notification.id)
            .where(UserNotification.user_id == user_id)
            .order_by(Notification.created_at.desc())
        )
        return result.all()


class UserNotificationRepository:

    async def bulk_create(
        self,
        db: AsyncSession,
        user_notifications,
    ) -> None:
        if user_notifications:
            db.add_all(user_notifications)
            await db.flush()

    async def mark_as_read(
        self,
        db: AsyncSession,
        notification_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> None:
        await db.execute(
            update(UserNotification)
            .where(UserNotification.notification_id == notification_id)
            .where(UserNotification.user_id == user_id)
            .values(is_read=True)
        )
        await db.commit()


class DeviceRepository:

    async def get_tokens(
        self,
        db: AsyncSession,
        user_ids,
    ) -> list[str]:
        if not user_ids:
            return []

        result = await db.execute(
            select(UserDevice.fcm_token).where(
                UserDevice.user_id.in_(user_ids)
            )
        )

        return result.scalars().all()