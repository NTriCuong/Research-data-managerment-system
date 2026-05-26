from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.auth.refresh_token import RefreshToken
from app.models.auth.user import User
from app.models.logs.login_log import LoginLog


class AuthRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def find_user_by_email_or_username_with_role(self, email_or_username: str) -> User | None:
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.role))
            .where((User.username == email_or_username) | (User.email == email_or_username))
        )
        return result.scalar_one_or_none()

    async def find_user_by_id_with_role(self, user_id: UUID) -> User | None:
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.role))
            .where(User.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def count_failed_logins_since(self, *, user_id: UUID, window_start: datetime) -> int:
        result = await self.db.execute(
            select(func.count())
            .select_from(LoginLog)
            .where(LoginLog.user_id == user_id)
            .where(LoginLog.login_result == "failed")
            .where(LoginLog.created_at >= window_start)
        )
        return int(result.scalar_one())

    async def add_login_log(
        self,
        *,
        user_id: UUID | None,
        username_attempted: str,
        login_result: str,
        failure_reason: str | None,
        ip_address: str | None,
        user_agent: str | None,
    ) -> None:
        self.db.add(
            LoginLog(
                user_id=user_id,
                username_attempted=username_attempted,
                login_result=login_result,
                failure_reason=failure_reason,
                ip_address=ip_address,
                user_agent=user_agent,
            )
        )

    async def add_refresh_token(
        self,
        *,
        user_id: UUID,
        token_hash: str,
        expires_at: datetime,
        ip_address: str | None,
        user_agent: str | None,
    ) -> None:
        self.db.add(
            RefreshToken(
                user_id=user_id,
                token_hash=token_hash,
                expires_at=expires_at,
                ip_address=ip_address,
                user_agent=user_agent,
            )
        )

    async def find_duplicate_user(self, *, username: str, email: str) -> User | None:
        result = await self.db.execute(select(User).where((User.username == username) | (User.email == email)))
        return result.scalar_one_or_none()

    async def create_user(self, user: User) -> User:
        self.db.add(user)
        await self.db.flush()
        return user

    async def get_active_refresh_tokens(self, user_id: UUID) -> list[RefreshToken]:
        result = await self.db.execute(
            select(RefreshToken)
            .where(RefreshToken.user_id == user_id)
            .where(RefreshToken.revoked_at.is_(None))
        )
        return result.scalars().all()


auth_repository = AuthRepository
