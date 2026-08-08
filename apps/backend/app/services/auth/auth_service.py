import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import (
    BadRequestException,
    ConfigurationException,
    ConflictException,
    ForbiddenException,
    NotFoundException,
    TooManyRequestsException,
    UnauthorizedException,
)
from app.models.auth.otp_verification import OtpVerification
from app.models.auth.refresh_token import RefreshToken
from app.models.auth.role import Role
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
from app.services.logs.login_log_service import login_log_service
from app.services.notification.email_service import email_service

OTP_TTL_MINUTES = 5


def _hash_otp(otp: str) -> str:
    return hashlib.sha256(f"{otp}{settings.OTP_SALT}".encode()).hexdigest()


def _generate_otp() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


class AuthService:
    @staticmethod
    def _validate_token_lifetime_policy() -> None:
        if settings.ACCESS_TOKEN_EXPIRE > 30:
            raise ConfigurationException("ACCESS_TOKEN_EXPIRE phải nhỏ hơn hoặc bằng 30 phút")
        if settings.REFRESH_TOKEN_EXPIRE > 7:
            raise ConfigurationException("REFRESH_TOKEN_EXPIRE phải nhỏ hơn hoặc bằng 7 ngày")

    async def list_users(
        self,
        db: AsyncSession,
        *,
        limit: int,
        offset: int,
        q: str | None,
        role_id: UUID | None,
        user_status: UserStatus | None,
    ) -> list[User]:
        return await AuthRepository(db).list_users(
            limit=limit,
            offset=offset,
            q=q,
            role_id=role_id,
            status=user_status.value if user_status else None,
        )

    async def list_roles(self, db: AsyncSession) -> list[Role]:
        return await AuthRepository(db).list_roles()

    async def get_user(self, db: AsyncSession, *, user_id: UUID) -> User:
        user = await AuthRepository(db).find_user_by_id_with_role(user_id)
        if user is None or user.deleted_at is not None:
            raise NotFoundException("Không tìm thấy người dùng")
        return user

    async def _ensure_role_exists(self, db: AsyncSession, role_id: UUID) -> None:
        if await AuthRepository(db).find_role_by_id(role_id) is None:
            raise BadRequestException("Không tìm thấy vai trò")

    # ── login ─────────────────────────────────────────────────────────────────

    async def login(
        self,
        db: AsyncSession,
        *,
        username: str,
        password: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> tuple[str, str, User]:
        """Xác thực người dùng. Trả về (access_token, raw_refresh_token, user).
        Client phải đặt raw_refresh_token làm cookie HttpOnly.
        """
        self._validate_token_lifetime_policy()
        repo = AuthRepository(db)
        user = await repo.find_user_by_email_or_username_with_role(username)

        async def _log(login_result: str, reason: str | None = None) -> None:
            await login_log_service.write_log(
                db,
                login_result=login_result,
                user_id=user.user_id if user else None,
                username_attempted=user.username if user else username,
                failure_reason=reason,
                ip_address=ip_address,
                user_agent=user_agent,
            )

        if user is None:
            await _log("failed", "Thông tin đăng nhập không hợp lệ")
            raise UnauthorizedException("Thông tin người dùng đăng nhập không tồn tại")

        if user.deleted_at is not None:
            await _log("failed", "Tài khoản đã bị xóa")
            raise ForbiddenException("Tài khoản đã bị xóa")

        if user.status != UserStatus.active:
            await _log("failed", "Tài khoản đã bị vô hiệu hóa")
            raise ForbiddenException("Tài khoản đã bị vô hiệu hóa")

        window_start = datetime.now(timezone.utc) - timedelta(minutes=settings.LOCK_DURATION)
        fail_count = await repo.count_failed_logins_since(user_id=user.user_id, window_start=window_start)
        if fail_count >= settings.MAX_LOGIN_ATTEMPTS:
            await _log("failed", "Tài khoản bị tạm khoá do sai mật khẩu quá nhiều lần")
            raise TooManyRequestsException(
                f"Đăng nhập thất bại quá nhiều lần. Vui lòng thử lại sau {settings.LOCK_DURATION} phút."
            )

        if not verify_password(password, user.password_hash):
            await _log("failed", "Thông tin đăng nhập không hợp lệ")
            raise UnauthorizedException("Thông tin đăng nhập không hợp lệ")

        user.last_login_at = datetime.now(timezone.utc)

        raw_rt, hashed_rt = create_refresh_token()
        await repo.add_refresh_token(
            user_id=user.user_id,
            issued_at=datetime.now(timezone.utc),
            token_hash=hashed_rt,
            expires_at=refresh_token_expires_at(),
            ip_address=ip_address,
            user_agent=user_agent,
        )

        access_token = create_access_token(str(user.user_id), user.role.role_code)
        await _log("success")
        return access_token, raw_rt, user

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
        repo = AuthRepository(db)
        if await repo.find_duplicate_user(username=username, email=email):
            raise ConflictException("Tên đăng nhập hoặc email đã tồn tại")

        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            full_name=full_name,
            role_id=role_id,
            department_id=department_id,
        )
        user = await repo.create_user(user)
        await db.flush()

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
        """Xoay vòng token: thu hồi token làm mới cũ, cấp cặp token truy cập + làm mới mới.
        Trả về (new_access_token, new_raw_refresh_token).
        """
        repo = AuthRepository(db)
        self._validate_token_lifetime_policy()

        db_token.revoked_at = datetime.now(timezone.utc)

        raw_rt, hashed_rt = create_refresh_token()

        await repo.add_refresh_token(
            user_id=user.user_id,
            issued_at=datetime.now(timezone.utc),
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

    # ── change_password ──────────────────────────────────────────────────────

    async def request_change_password(
        self,
        db: AsyncSession,
        *,
        user: User,
        current_password: str,
        new_password: str,
    ) -> None:
        if not verify_password(current_password, user.password_hash):
            raise BadRequestException("Mật khẩu hiện tại không chính xác")

        if current_password == new_password:
            raise BadRequestException("Mật khẩu mới không được trùng mật khẩu cũ")

        repo = AuthRepository(db)
        await repo.delete_otp_by_user(user.user_id)

        otp_code = _generate_otp()
        repo.add_otp(
            OtpVerification(
                user_id=user.user_id,
                otp_hash=_hash_otp(otp_code),
                old_password_hash=user.password_hash,
                new_password_hash=hash_password(new_password),
                expires_at=datetime.now(timezone.utc) + timedelta(minutes=OTP_TTL_MINUTES),
            )
        )
        await db.commit()

        await email_service.send_email(
            to_email=user.email,
            subject="Mã xác thực đổi mật khẩu",
            body=f"Mã OTP của bạn là: {otp_code}. Mã có hiệu lực trong {OTP_TTL_MINUTES} phút.",
        )

    async def confirm_change_password(
        self,
        db: AsyncSession,
        *,
        user: User,
        otp_code: str,
    ) -> None:
        repo = AuthRepository(db)
        otp_row = await repo.find_latest_otp_by_user(user.user_id)

        if not otp_row or otp_row.expires_at < datetime.now(timezone.utc):
            raise BadRequestException("Mã OTP không tồn tại hoặc đã hết hạn")

        if _hash_otp(otp_code) != otp_row.otp_hash:
            raise BadRequestException("Mã OTP không chính xác")

        if user.password_hash != otp_row.old_password_hash:
            raise BadRequestException("Mật khẩu đã bị thay đổi, vui lòng thực hiện lại từ đầu")

        deleted_count = await repo.delete_otp_by_id(otp_row.id)
        if deleted_count == 0:
            raise BadRequestException("Mã OTP đã được sử dụng")

        user.password_hash = otp_row.new_password_hash
        user.updated_at = datetime.now(timezone.utc)
        await self.revoke_all_sessions(db, user_id=user.user_id)
        await db.commit()

        await audit_service.write_log(
            db,
            action_code="CHANGE_PASSWORD",
            actor_user_id=user.user_id,
            target_schema="auth",
            target_table="users",
            target_id=user.user_id,
            result="success",
        )

    # ── admin user management ────────────────────────────────────────────────

    async def create_user(
        self,
        db: AsyncSession,
        *,
        actor: User,
        username: str,
        email: str,
        password: str,
        full_name: str,
        role_id: UUID,
        department_id: UUID | None = None,
    ) -> User:
        await self._ensure_role_exists(db, role_id)
        user = await self.register(
            db,
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            role_id=role_id,
            department_id=department_id,
        )
        await audit_service.write_log(
            db,
            action_code="ADMIN_CREATE_USER",
            actor_user_id=actor.user_id,
            target_schema="auth",
            target_table="users",
            target_id=user.user_id,
            new_value={"username": username, "email": email, "role_id": str(role_id)},
            result="success",
            message="Admin created user",
        )
        return user

    async def update_user(
        self,
        db: AsyncSession,
        *,
        actor: User,
        user_id: UUID,
        username: str | None = None,
        email: str | None = None,
        full_name: str | None = None,
        department_id: UUID | None = None,
        fields_set: set[str] | None = None,
    ) -> User:
        repo = AuthRepository(db)
        user = await repo.find_user_by_id_with_role(user_id)
        if user is None or user.deleted_at is not None:
            raise NotFoundException("Không tìm thấy người dùng")
        changed_old: dict = {}
        changed_new: dict = {}

        if username is not None and username != user.username:
            existing = await repo.find_user_by_username(username)
            if existing is not None and existing.user_id != user.user_id:
                raise ConflictException("Tên đăng nhập đã tồn tại")
            changed_old["username"] = user.username
            changed_new["username"] = username
            user.username = username
        if email is not None and email != user.email:
            existing = await repo.find_user_by_email(email)
            if existing is not None and existing.user_id != user.user_id:
                raise ConflictException("Email đã tồn tại")
            changed_old["email"] = user.email
            changed_new["email"] = email
            user.email = email
        if full_name is not None and full_name != user.full_name:
            changed_old["full_name"] = user.full_name
            changed_new["full_name"] = full_name
            user.full_name = full_name
        if fields_set and "department_id" in fields_set and department_id != user.department_id:
            changed_old["department_id"] = str(user.department_id) if user.department_id else None
            changed_new["department_id"] = str(department_id) if department_id else None
            user.department_id = department_id

        if changed_new:
            user.updated_at = datetime.now(timezone.utc)
            await audit_service.write_log(
                db,
                action_code="ADMIN_UPDATE_USER",
                actor_user_id=actor.user_id,
                target_schema="auth",
                target_table="users",
                target_id=user.user_id,
                old_value=changed_old,
                new_value=changed_new,
                result="success",
                message="Admin updated user profile",
            )
        return user

    async def soft_delete_user(self, db: AsyncSession, *, actor: User, user_id: UUID) -> None:
        repo = AuthRepository(db)
        user = await repo.find_user_by_id_with_role(user_id)
        if user is None or user.deleted_at is not None:
            raise NotFoundException("Không tìm thấy người dùng")
        if user.user_id == actor.user_id:
            raise BadRequestException("Không thể xóa tài khoản đang đăng nhập")
        now = datetime.now(timezone.utc)
        user.deleted_at = now
        user.updated_at = now
        await self.revoke_all_sessions(db, user_id=user.user_id)
        await audit_service.write_log(
            db,
            action_code="ADMIN_SOFT_DELETE_USER",
            actor_user_id=actor.user_id,
            target_schema="auth",
            target_table="users",
            target_id=user.user_id,
            old_value={"deleted_at": None},
            new_value={"deleted_at": now.isoformat()},
            result="success",
            message="Admin soft-deleted user",
        )

    async def update_user_role(self, db: AsyncSession, *, actor: User, user_id: UUID, role_id: UUID) -> User:
        await self._ensure_role_exists(db, role_id)
        repo = AuthRepository(db)
        user = await repo.find_user_by_id_with_role(user_id)
        if user is None or user.deleted_at is not None:
            raise NotFoundException("Không tìm thấy người dùng")
        old_role_id = user.role_id
        user.role_id = role_id
        user.updated_at = datetime.now(timezone.utc)
        await self.revoke_all_sessions(db, user_id=user.user_id)
        await audit_service.write_log(
            db,
            action_code="ADMIN_ASSIGN_ROLE",
            actor_user_id=actor.user_id,
            target_schema="auth",
            target_table="users",
            target_id=user.user_id,
            old_value={"role_id": str(old_role_id)},
            new_value={"role_id": str(role_id)},
            result="success",
            message="Admin changed user role",
        )
        return user

    async def update_user_status(self, db: AsyncSession, *, actor: User, user_id: UUID, new_status: UserStatus) -> User:
        repo = AuthRepository(db)
        user = await repo.find_user_by_id_with_role(user_id)
        if user is None or user.deleted_at is not None:
            raise NotFoundException("Không tìm thấy người dùng")
        old_status = user.status
        user.status = new_status
        user.updated_at = datetime.now(timezone.utc)
        if new_status != UserStatus.active:
            await self.revoke_all_sessions(db, user_id=user.user_id)
        await audit_service.write_log(
            db,
            action_code="ADMIN_UPDATE_USER_STATUS",
            actor_user_id=actor.user_id,
            target_schema="auth",
            target_table="users",
            target_id=user.user_id,
            old_value={"status": old_status.value},
            new_value={"status": new_status.value},
            result="success",
            message="Admin updated user status",
        )
        return user

    async def admin_reset_password(
        self,
        db: AsyncSession,
        *,
        actor: User,
        user_id: UUID,
        new_password: str,
    ) -> None:
        repo = AuthRepository(db)
        user = await repo.find_user_by_id_with_role(user_id)
        if user is None or user.deleted_at is not None:
            raise NotFoundException("Không tìm thấy người dùng")
        user.password_hash = hash_password(new_password)
        user.updated_at = datetime.now(timezone.utc)
        await self.revoke_all_sessions(db, user_id=user.user_id)
        await audit_service.write_log(
            db,
            action_code="ADMIN_RESET_PASSWORD",
            actor_user_id=actor.user_id,
            target_schema="auth",
            target_table="users",
            target_id=user.user_id,
            result="success",
            message="Admin reset user password",
        )


auth_service = AuthService()