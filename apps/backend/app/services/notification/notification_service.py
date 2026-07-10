import logging
from html import escape
from urllib.parse import urljoin
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.models.auth.role import Role
from app.models.auth.user import User
from app.models.enum import UserStatus
from app.repositories.notification_repository import DeviceRepository, NotificationRepository
from app.schemas.notification import NotificationOut
from app.services.notification.email_service import email_service
from app.services.notification.fcm_service import fcm_service

logger = logging.getLogger(__name__)

_notification_repo = NotificationRepository()
_device_repo = DeviceRepository()


async def push_to_users(db: AsyncSession, user_ids: list[UUID], title: str, message: str) -> None:
    tokens = await _device_repo.get_tokens(db, list(user_ids))
    logger.info("FCM push_to_users: %d user(s), %d token(s)", len(user_ids), len(tokens))
    if tokens:
        await fcm_service.send(list(tokens), title, message)


async def push_to_roles(db: AsyncSession, role_codes: list[str], title: str, message: str) -> None:
    result = await db.execute(
        select(User.user_id)
        .join(Role, Role.role_id == User.role_id)
        .where(Role.role_code.in_(role_codes))
        .where(User.deleted_at.is_(None))
    )
    user_ids = [row[0] for row in result.all()]
    logger.info("FCM push_to_roles %s: %d user(s) found", role_codes, len(user_ids))
    await push_to_users(db, user_ids, title, message)


class NotificationService:
    @staticmethod
    def _absolute_target_url(target_url: str | None) -> str | None:
        if not target_url:
            return None
        return urljoin(settings.FRONTEND_URL.rstrip("/") + "/", target_url.lstrip("/"))

    @staticmethod
    def _notification_html_body(*, message: str, absolute_url: str | None) -> str:
        safe_message = escape(message)
        if not absolute_url:
            return f"<p>{safe_message}</p>"

        safe_url = escape(absolute_url, quote=True)
        return f"""
        <div style="font-family: Arial, sans-serif; line-height: 1.5; color: #111827;">
            <p>{safe_message}</p>
            <p>
                <a href="{safe_url}" style="color: #1d4ed8; font-weight: 600;">
                    Xem chi tiết
                </a>
            </p>
        </div>
        """.strip()

    async def list_my_notifications(
        self,
        db: AsyncSession,
        *,
        current_user: User,
        limit: int,
        offset: int,
        unread_only: bool,
    ) -> list[NotificationOut]:
        rows = await _notification_repo.get_by_user(
            db,
            user_id=current_user.user_id,
            limit=limit,
            offset=offset,
            unread_only=unread_only,
        )
        return [
            NotificationOut(
                notification_id=user_notification_id,
                event_type=notification_type,
                title=title,
                message=message,
                target_url=action_url,
                read_at=read_at,
                created_at=created_at,
            )
            for (
                user_notification_id,
                notification_type,
                title,
                message,
                action_url,
                read_at,
                created_at,
            ) in rows
        ]

    async def mark_read(
        self,
        db: AsyncSession,
        *,
        notification_id: UUID,
        current_user: User,
    ) -> NotificationOut | None:
        result = await _notification_repo.mark_read(
            db,
            user_notification_id=notification_id,
            user_id=current_user.user_id,
        )
        if result is None:
            return None
        user_notification, notification = result
        return NotificationOut(
            notification_id=user_notification.id,
            event_type=notification.notification_type,
            title=notification.title,
            message=notification.message,
            target_url=notification.action_url,
            read_at=user_notification.read_at,
            created_at=notification.created_at,
        )

    async def notify_role(
        self,
        db: AsyncSession,
        *,
        role_codes: list[str],
        actor_user_id: UUID | None,
        event_type: str,
        title: str,
        message: str,
        target_url: str | None,
        payload: dict | None = None,
    ) -> None:
        users = (
            await db.execute(
                select(User)
                .join(Role, Role.role_id == User.role_id)
                .options(selectinload(User.role))
                .where(Role.role_code.in_(role_codes))
                .where(User.deleted_at.is_(None))
                .where(User.status == UserStatus.active)
            )
        ).scalars().all()
        await self._notify_users(
            db,
            users=users,
            actor_user_id=actor_user_id,
            event_type=event_type,
            title=title,
            message=message,
            target_url=target_url,
            payload=payload,
        )

    async def notify_user(
        self,
        db: AsyncSession,
        *,
        recipient_user_id: UUID,
        actor_user_id: UUID | None,
        event_type: str,
        title: str,
        message: str,
        target_url: str | None,
        payload: dict | None = None,
    ) -> None:
        user = (
            await db.execute(
                select(User)
                .where(User.user_id == recipient_user_id)
                .where(User.deleted_at.is_(None))
                .where(User.status == UserStatus.active)
            )
        ).scalar_one_or_none()
        if user is None:
            return
        await self._notify_users(
            db,
            users=[user],
            actor_user_id=actor_user_id,
            event_type=event_type,
            title=title,
            message=message,
            target_url=target_url,
            payload=payload,
        )

    async def _notify_users(
        self,
        db: AsyncSession,
        *,
        users: list[User],
        actor_user_id: UUID | None,
        event_type: str,
        title: str,
        message: str,
        target_url: str | None,
        payload: dict | None,
    ) -> None:
        if not users:
            return

        absolute_url = self._absolute_target_url(target_url)
        recipient_ids: list[UUID] = []
        seen: set[UUID] = set()
        for user in users:
            if user.user_id in seen:
                continue
            seen.add(user.user_id)
            recipient_ids.append(user.user_id)
            await email_service.send_email(
                to_email=user.email,
                subject=title,
                body=f"{message}\n\nXem chi tiet: {absolute_url or ''}".strip(),
                html_body=self._notification_html_body(
                    message=message,
                    absolute_url=absolute_url,
                ),
            )

        await _notification_repo.create_for_recipients(
            db,
            title=title,
            message=message,
            notification_type=event_type,
            action_url=target_url,
            sender_user_id=actor_user_id,
            payload=payload,
            recipient_user_ids=recipient_ids,
        )


notification_service = NotificationService()
