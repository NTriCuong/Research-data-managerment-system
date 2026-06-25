import firebase_admin
from firebase_admin import credentials, messaging

from app.models.notification.notification import Notification
from app.models.notification.user_notification import UserNotification

# init firebase (chỉ chạy 1 lần)
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase-service-account.json")
    firebase_admin.initialize_app(cred)


class FCMService:

    def send(self, tokens, title, message):
        if not tokens:
            return None

        # Firebase multicast 
        msg = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=message
            ),
            tokens=tokens
        )

        response = messaging.send_multicast(msg)
        return response



class NotificationService:

    def __init__(self, noti_repo, user_noti_repo, device_repo, fcm_service):
        self.noti_repo = noti_repo
        self.user_noti_repo = user_noti_repo
        self.device_repo = device_repo
        self.fcm_service = fcm_service

    def notify(
        self,
        db,
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

        notification = self.noti_repo.create(db, notification)

        # 2. create user_notifications
        user_notifications = [
            UserNotification(
                user_id=u,
                notification_id=notification.id
            )
            for u in user_ids
        ]

        self.user_noti_repo.bulk_create(db, user_notifications)

        # 3. get tokens
        tokens = self.device_repo.get_tokens(db, user_ids)

        # 4. send FCM
        self.fcm_service.send(tokens, title, message)

        # 5. commit transaction
        db.commit()

        return notification