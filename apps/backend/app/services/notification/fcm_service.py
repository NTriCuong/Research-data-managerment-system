import asyncio
import os
import firebase_admin
from firebase_admin import credentials, messaging



# =========================
# INIT FIREBASE (SAFE)
# =========================
if not firebase_admin._apps:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    FIREBASE_PATH = os.path.join(BASE_DIR, "firebase-service-account.json")

    if not os.path.exists(FIREBASE_PATH):
        raise FileNotFoundError(f"Firebase file not found: {FIREBASE_PATH}")

    cred = credentials.Certificate(FIREBASE_PATH)
    firebase_admin.initialize_app(cred)


# =========================
# FCM SERVICE
# =========================
class FCMService:

    async def send(self, tokens, title, message):
        if not tokens:
            return None

        msg = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=message
            ),
            data={"type": "NEW_NOTIFICATION"},
            tokens=tokens
        )

        return await asyncio.to_thread(messaging.send_multicast, msg)

fcm_service = FCMService()