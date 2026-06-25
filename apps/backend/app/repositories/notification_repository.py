class NotificationRepository:

    def create(self, db, notification):
        db.add(notification)
        db.flush()  # lấy ID ngay lập tức
        return notification

class UserNotificationRepository:

    def bulk_create(self, db, user_notifications):
        if user_notifications:
            db.add_all(user_notifications)
from app.models.notification.user_device import UserDevice


class DeviceRepository:

    def get_tokens(self, db, user_ids):
        if not user_ids:
            return []

        devices = db.query(UserDevice.fcm_token).filter(
            UserDevice.user_id.in_(user_ids)
        ).all()

        return [d[0] for d in devices]