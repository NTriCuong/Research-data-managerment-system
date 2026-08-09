import logging
import firebase_admin
from firebase_admin import credentials, messaging

from app.core.config import settings

logger = logging.getLogger(__name__)


def _ensure_firebase_initialized() -> bool:
    if firebase_admin._apps:
        return True
    try:
        cred = credentials.Certificate(str(settings.FIREBASE_CREDENTIALS_PATH))
        firebase_admin.initialize_app(cred)
        logger.info("Firebase initialized successfully")
        return True
    except FileNotFoundError:
        logger.warning("Firebase credentials not found at %s; FCM push disabled", settings.FIREBASE_CREDENTIALS_PATH)
        return False
    except Exception as e:
        logger.error("Firebase init failed: %s", e)
        return False


class FCMService:

    async def send(self, tokens: list[str], title: str, message: str):
        if not tokens:
            return None
        if not _ensure_firebase_initialized():
            return None

        msg = messaging.MulticastMessage(
            notification=messaging.Notification(title=title, body=message),
            data={"type": "NEW_NOTIFICATION"},
            tokens=tokens,
        )
        response = await messaging.send_each_for_multicast_async(msg)
        logger.info("FCM sent to %d token(s): success=%d, failure=%d",
                    len(tokens), response.success_count, response.failure_count)
        return response


fcm_service = FCMService()
