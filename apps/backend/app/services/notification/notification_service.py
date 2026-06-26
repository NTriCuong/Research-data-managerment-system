from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reference.notification import Notification
from app.models.reference.user_notification import UserNotification
from app.repositories.notification_repository import (
    NotificationRepository,
    UserNotificationRepository,
    DeviceRepository,
)
from app.services.notification.fcm_service import fcm_service


# NOTIFICATION SERVICE
class NotificationService:

    def __init__(self, noti_repo, user_noti_repo, device_repo, fcm_service):
        self.noti_repo = noti_repo
        self.user_noti_repo = user_noti_repo
        self.device_repo = device_repo
        self.fcm_service = fcm_service

    # CREATE + SEND NOTIFICATION
    async def notify(
        self,
        db: AsyncSession,
        user_ids,
        title,
        message,
        type_,
        sender_id=None,
        research_id=None
    ):

        # 1. create notification
        notification = Notification(
            title=title,
            message=message,
            notification_type=type_,
            sender_user_id=sender_id,
            research_id=research_id
        )

        notification = await self.noti_repo.create(db, notification)

        # 2. create user_notifications
        user_notifications = [
            UserNotification(
                user_id=u,
                notification_id=notification.id
            )
            for u in user_ids
        ]

        await self.user_noti_repo.bulk_create(db, user_notifications)

        # 3. get tokens
        tokens = await self.device_repo.get_tokens(db, user_ids)

        # 4. send FCM
        await self.fcm_service.send(tokens, title, message)

        # 5. commit transaction
        await db.commit()

        return notification

    # GET NOTIFICATIONS BY USER
    async def get_notifications(self, db: AsyncSession, user_id):
        rows = await self.noti_repo.get_by_user(db, user_id)
        return [
            {
                "id": str(n.id),
                "title": n.title,
                "message": n.message,
                "notification_type": n.notification_type,
                "research_id": str(n.research_id) if n.research_id else None,
                "is_read": is_read,
                "created_at": n.created_at,
            }
            for n, is_read in rows
        ]

    # MARK AS READ
    async def mark_as_read(self, db: AsyncSession, notification_id, user_id):
        await self.user_noti_repo.mark_as_read(db, notification_id, user_id)


notification_service = NotificationService(
    noti_repo=NotificationRepository(),
    user_noti_repo=UserNotificationRepository(),
    device_repo=DeviceRepository(),
    fcm_service=fcm_service,
)