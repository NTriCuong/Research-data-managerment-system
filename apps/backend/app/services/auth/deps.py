from datetime import datetime, timezone
from uuid import UUID

from fastapi import Cookie, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.session import get_db
from app.models.auth.user import User
from app.models.auth.refresh_token import RefreshToken
from app.models.enum import UserStatus
from app.services.auth.security import decode_access_token, hash_refresh_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# ── RBAC permission map ───────────────────────────────────────────────────────
# Key = role_code trong bảng auth.roles (khớp seed data)

ROLE_PERMISSIONS: dict[str, set[str]] = {
    "SUPER_ADMIN": {"*"},
    "DATA_ENTRY":  {"research:read", "research:write", "file:write"},
    "REVIEWER":    {"research:read", "research:review"},
    "APPROVER":    {"research:read", "research:approve"},
    "MANAGER":     {"research:read", "dashboard:read", "report:read"},
    "PUBLIC_USER": {"research:read"},
}


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _load_user(db: AsyncSession, user_id: str) -> User | None:
    """Load user kèm role relationship bằng một query."""
    try:
        uid = UUID(user_id)
    except ValueError:
        return None
    result = await db.execute(
        select(User)
        .options(selectinload(User.role))
        .where(User.user_id == uid)
    )
    return result.scalar_one_or_none()


# ── get_current_user ──────────────────────────────────────────────────────────

async def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        if payload.get("type") != "access":
            raise credentials_exc
        user_id: str | None = payload.get("sub")
        if not user_id:
            raise credentials_exc
    except JWTError:
        raise credentials_exc

    user = await _load_user(db, user_id)
    if user is None:
        raise credentials_exc

    request.state.current_user_id = str(user.user_id)
    return user


# ── get_current_active_user ───────────────────────────────────────────────────

async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account has been deleted")
    if current_user.status != UserStatus.active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled")
    return current_user


# ── Refresh token from HttpOnly cookie ───────────────────────────────────────

async def get_valid_refresh_token(
    refresh_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
) -> tuple[RefreshToken, User]:
    """Đọc refresh token từ HttpOnly cookie, xác minh với DB.
    Trả về (RefreshToken record, User) nếu hợp lệ.
    """
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing refresh token",
        )

    token_hash = hash_refresh_token(refresh_token)
    result = await db.execute(
        select(RefreshToken)
        .options(selectinload(RefreshToken.user).selectinload(User.role))
        .where(RefreshToken.token_hash == token_hash)
        .where(RefreshToken.revoked_at.is_(None))
    )
    db_token = result.scalar_one_or_none()

    if db_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked refresh token",
        )

    if db_token.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired",
        )

    user = db_token.user
    if user.deleted_at is not None or user.status != UserStatus.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )

    return db_token, user


# ── RoleChecker ───────────────────────────────────────────────────────────────

class RoleChecker:
    def __init__(self, permission: str):
        self.permission = permission

    async def __call__(
        self,
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        role_code = current_user.role.role_code
        allowed = ROLE_PERMISSIONS.get(role_code, set())

        if "*" in allowed:
            return current_user

        if self.permission not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role_code}' does not have permission '{self.permission}'",
            )
        return current_user


# ── Shorthand dependencies ────────────────────────────────────────────────────

require_login          = Depends(get_current_active_user)
require_research_read  = Depends(RoleChecker("research:read"))
require_research_write = Depends(RoleChecker("research:write"))
require_research_review = Depends(RoleChecker("research:review"))
require_research_approve = Depends(RoleChecker("research:approve"))
require_dashboard_read = Depends(RoleChecker("dashboard:read"))
require_report_read    = Depends(RoleChecker("report:read"))
require_file_write     = Depends(RoleChecker("file:write"))
