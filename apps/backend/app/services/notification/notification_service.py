import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.notification_repository import DeviceRepository
from app.services.notification.fcm_service import fcm_service

logger = logging.getLogger(__name__)

_device_repo = DeviceRepository()


async def push_to_users(db: AsyncSession, user_ids: list[UUID], title: str, message: str) -> None:
    tokens = await _device_repo.get_tokens(db, list(user_ids))
    logger.info("FCM push_to_users: %d user(s), %d token(s)", len(user_ids), len(tokens))
    if tokens:
        await fcm_service.send(list(tokens), title, message)


async def push_to_roles(db: AsyncSession, role_codes: list[str], title: str, message: str) -> None:
    from sqlalchemy import select
    from app.models.auth.role import Role
    from app.models.auth.user import User

    result = await db.execute(
        select(User.user_id)
        .join(Role, Role.role_id == User.role_id)
        .where(Role.role_code.in_(role_codes))
        .where(User.deleted_at.is_(None))
    )
    user_ids = [row[0] for row in result.all()]
    logger.info("FCM push_to_roles %s: %d user(s) found", role_codes, len(user_ids))
    await push_to_users(db, user_ids, title, message)
