import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reference.notification import FCMNotification as Notification
from app.models.reference.user_device import UserDevice
from app.models.reference.user_notification import UserNotification


class NotificationRepository:

    async def create_for_recipients(
        self,
        db: AsyncSession,
        *,
        title: str,
        message: str,
        notification_type: str,
        action_url: str | None,
        sender_user_id: uuid.UUID | None,
        payload: dict | None,
        recipient_user_ids: list[uuid.UUID],
    ) -> Notification | None:
        recipient_ids = list(dict.fromkeys(recipient_user_ids))
        if not recipient_ids:
            return None

        notification = Notification(
            title=title,
            message=message,
            notification_type=notification_type,
            action_url=action_url,
            sender_user_id=sender_user_id,
            payload=payload,
        )
        db.add(notification)
        await db.flush()

        db.add_all(
            UserNotification(notification_id=notification.id, user_id=recipient_id)
            for recipient_id in recipient_ids
        )
        await db.flush()
        return notification

    async def get_by_user(
        self,
        db: AsyncSession,
        *,
        user_id: uuid.UUID,
        limit: int,
        offset: int,
        unread_only: bool,
    ) -> list:
        stmt = (
            select(
                UserNotification.id,
                Notification.notification_type,
                Notification.title,
                Notification.message,
                Notification.action_url,
                UserNotification.read_at,
                Notification.created_at,
            )
            .join(Notification, Notification.id == UserNotification.notification_id)
            .where(UserNotification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        if unread_only:
            stmt = stmt.where(UserNotification.read_at.is_(None))
        result = await db.execute(stmt)
        return result.all()

    async def mark_read(
        self,
        db: AsyncSession,
        *,
        user_notification_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> tuple[UserNotification, Notification] | None:
        stmt = (
            select(UserNotification, Notification)
            .join(Notification, Notification.id == UserNotification.notification_id)
            .where(UserNotification.id == user_notification_id)
            .where(UserNotification.user_id == user_id)
        )
        row = (await db.execute(stmt)).one_or_none()
        if row is None:
            return None
        user_notification, notification = row
        if user_notification.read_at is None:
            user_notification.read_at = datetime.now(timezone.utc)
            await db.flush()
        return user_notification, notification


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
