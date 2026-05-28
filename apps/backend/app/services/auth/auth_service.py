from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.auth.refresh_token import RefreshToken
from app.models.auth.user import User
from app.models.enum import UserStatus
from app.repositories.auth_repository import AuthRepository
from app.services.auth.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    refresh_token_expires_at,
    verify_password,
)
from app.services.logs.audit_service import audit_service


class AuthService:

    # ── login ─────────────────────────────────────────────────────────────────

    async def login(
        self,
        db: AsyncSession,
        *,
        email: str,
        password: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> tuple[str, str]:
        """Xác thực người dùng. Trả về (access_token, raw_refresh_token).
        Client phải đặt raw_refresh_token làm cookie HttpOnly.
        """
        repo = AuthRepository(db)
        user = await repo.find_user_by_email_or_username_with_role(email)

        async def _log(login_result: str, reason: str | None = None) -> None:
            await repo.add_login_log(
                login_result=login_result,
                user_id=user.user_id if user else None,
                username_attempted=user.username if user else email,  # fallback email nếu user không tồn tại
                failure_reason=reason,
                ip_address=ip_address,
                user_agent=user_agent,
            )

        if user is None:
            await _log("failed", "user_not_found")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        if user.deleted_at is not None:
            await _log("failed", "account_deleted")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account has been deleted",
            )

        if user.status != UserStatus.active:
            await _log("failed", "account_disabled")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled",
            )

        # Brute-force lockout
        window_start = datetime.now(timezone.utc) - timedelta(minutes=settings.LOCK_DURATION)
        fail_count = await repo.count_failed_logins_since(user_id=user.user_id, window_start=window_start)
        if fail_count >= settings.MAX_LOGIN_ATTEMPTS:
            await _log("failed", "account_locked")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many failed attempts. Try again after {settings.LOCK_DURATION} minutes.",
            )

        if not verify_password(password, user.password_hash):
            await _log("failed", "wrong_password")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        # Issue tokens
        user.last_login_at = datetime.now(timezone.utc)

        raw_rt, hashed_rt = create_refresh_token()
        await repo.add_refresh_token(
            user_id=user.user_id,
            token_hash=hashed_rt,
            expires_at=refresh_token_expires_at(),
            ip_address=ip_address,
            user_agent=user_agent,
        )

        access_token = create_access_token(str(user.user_id), user.role.role_code)
        await _log("success")
        return access_token, raw_rt

    # ── register ──────────────────────────────────────────────────────────────

    async def register(
        self,
        db: AsyncSession,
        *,
        username: str,
        email: str,
        password: str,
        full_name: str,
        role_id: UUID,
        department_id: UUID | None = None,
    ) -> User:
        """Create a new user. Raises 409 if username or email is already taken."""
        repo = AuthRepository(db)
        if await repo.find_duplicate_user(username=username, email=email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username or email already exists",
            )

        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            full_name=full_name,
            role_id=role_id,
            department_id=department_id,
        )
        user = await repo.create_user(user)
        await db.flush()  # sau dòng này user.user_id đã có

        await audit_service.write_log(
            db,
            action_code="CREATE_USER",
            actor_user_id=None,
            target_schema="auth",
            target_table="users",
            target_id=user.user_id,
            new_value={"username": username, "email": email, "role_id": str(role_id)},
            result="success",
        )

        return user

    # ── refresh_token ─────────────────────────────────────────────────────────

    async def refresh_token(
        self,
        db: AsyncSession,
        *,
        db_token: RefreshToken,
        user: User,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> tuple[str, str]:
        """Token rotation: revoke old refresh token, issue new access + refresh pair.
        Returns (new_access_token, new_raw_refresh_token).
        """
        repo = AuthRepository(db)
        db_token.revoked_at = datetime.now(timezone.utc)
        raw_rt, hashed_rt = create_refresh_token()
        await repo.add_refresh_token(
            user_id=user.user_id,
            token_hash=hashed_rt,
            expires_at=refresh_token_expires_at(),
            ip_address=ip_address,
            user_agent=user_agent,
        )

        access_token = create_access_token(str(user.user_id), user.role.role_code)
        return access_token, raw_rt

    # ── logout ────────────────────────────────────────────────────────────────

    async def logout(
        self,
        db: AsyncSession,
        *,
        db_token: RefreshToken,
    ) -> None:
        """Revoke refresh token hiện tại."""
        db_token.revoked_at = datetime.now(timezone.utc)

    # ── revoke_all_sessions ───────────────────────────────────────────────────

    async def revoke_all_sessions(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
    ) -> int:
        """Revoke all active refresh tokens for a user. Returns number of revoked tokens."""
        repo = AuthRepository(db)
        tokens = await repo.get_active_refresh_tokens(user_id)

        now = datetime.now(timezone.utc)
        for token in tokens:
            token.revoked_at = now
        return len(tokens)

    # ── change_password ───────────────────────────────────────────────────────

    async def change_password(
        self,
        db: AsyncSession,
        *,
        user: User,
        old_password: str,
        new_password: str,
    ) -> None:
        """Verify mật khẩu cũ, cập nhật hash, revoke toàn bộ session."""
        if not verify_password(old_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )

        user.password_hash = hash_password(new_password)
        user.updated_at = datetime.now(timezone.utc)
        await self.revoke_all_sessions(db, user_id=user.user_id)

        await audit_service.write_log(
            db,
            action_code="CHANGE_PASSWORD",
            actor_user_id=user.user_id,
            target_schema="auth",
            target_table="users",
            target_id=user.user_id,
            result="success",
        )

auth_service = AuthService()
