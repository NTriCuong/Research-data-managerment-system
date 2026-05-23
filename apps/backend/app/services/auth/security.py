import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt

from app.services.auth.config import settings


# ── Password ──────────────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


# ── Access token ──────────────────────────────────────────────────────────────

def create_access_token(user_id: str, role_code: str) -> str:
    """JWT access token — gửi trong body response."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE
    )
    payload = {
        "sub": user_id,
        "role": role_code,
        "type": "access",
        "exp": expire,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Raises jose.JWTError nếu token không hợp lệ hoặc hết hạn."""
    return jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )


# ── Refresh token ─────────────────────────────────────────────────────────────
# Refresh token là chuỗi ngẫu nhiên 48-byte — không phải JWT.
# - Giá trị raw gửi cho client qua HttpOnly cookie.
# - SHA-256 hash lưu vào bảng auth.refresh_tokens (token_hash).
# Dùng SHA-256 (không phải bcrypt) vì token đã có entropy 384-bit — overhead
# của bcrypt là không cần thiết.

def create_refresh_token() -> tuple[str, str]:
    """Trả về (raw_token, hashed_token).
    Lưu hashed_token vào DB, gửi raw_token cho client.
    """
    raw = secrets.token_urlsafe(48)
    hashed = _sha256(raw)
    return raw, hashed


def hash_refresh_token(raw: str) -> str:
    return _sha256(raw)


def refresh_token_expires_at() -> datetime:
    return datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE)


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()
