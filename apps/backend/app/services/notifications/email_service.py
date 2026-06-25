import logging
import smtplib
from email.message import EmailMessage

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    async def send_email(self, *, to_email: str, subject: str, body: str, html_body: str | None = None) -> None:
        if not settings.SMTP_HOST or not settings.SMTP_FROM_EMAIL:
            logger.warning("SMTP is not configured; skip notification email to %s", to_email)
            return

        message = EmailMessage()
        message["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
        message["To"] = to_email
        message["Subject"] = subject
        message.set_content(body)
        if html_body:
            message.add_alternative(html_body, subtype="html")

        try:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as smtp:
                if settings.SMTP_USE_TLS:
                    smtp.starttls()
                if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
                    smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD.replace(" ", ""))
                smtp.send_message(message)
                logger.info("Sent notification email to %s", to_email)
        except Exception:
            logger.exception("Failed to send notification email to %s", to_email)


email_service = EmailService()
