from datetime import datetime, timezone
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
from app.models.logs.notification import Notification
from app.schemas.notification import NotificationOut
from app.services.notifications.email_service import email_service


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
                    Xem chi tiet
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
        stmt = (
            select(Notification)
            .where(Notification.recipient_user_id == current_user.user_id)
            .order_by(Notification.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        if unread_only:
            stmt = stmt.where(Notification.read_at.is_(None))
        rows = (await db.execute(stmt)).scalars().all()
        return [NotificationOut.model_validate(row) for row in rows]

    async def mark_read(
        self,
        db: AsyncSession,
        *,
        notification_id: UUID,
        current_user: User,
    ) -> NotificationOut | None:
        notification = (
            await db.execute(
                select(Notification)
                .where(Notification.notification_id == notification_id)
                .where(Notification.recipient_user_id == current_user.user_id)
            )
        ).scalar_one_or_none()
        if notification is None:
            return None
        if notification.read_at is None:
            notification.read_at = datetime.now(timezone.utc)
            await db.flush()
            await db.refresh(notification)
        return NotificationOut.model_validate(notification)

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
        seen: set[UUID] = set()
        absolute_url = self._absolute_target_url(target_url)
        for user in users:
            if user.user_id in seen:
                continue
            seen.add(user.user_id)
            db.add(
                Notification(
                    recipient_user_id=user.user_id,
                    actor_user_id=actor_user_id,
                    event_type=event_type,
                    title=title,
                    message=message,
                    target_url=target_url,
                    payload=payload,
                )
            )
            await email_service.send_email(
                to_email=user.email,
                subject=title,
                body=f"{message}\n\nXem chi tiet: {absolute_url or ''}".strip(),
                html_body=self._notification_html_body(
                    message=message,
                    absolute_url=absolute_url,
                ),
            )


notification_service = NotificationService()
