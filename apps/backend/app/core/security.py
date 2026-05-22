from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

# ── Password hashing ─────────────────────────────────────────────────────────

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(passWord: str) -> str:
    """Bcrypt hash — salt được sinh ngẫu nhiên, nhúng trong chuỗi kết quả."""
    return pwd_context.hash(passWord)

def verify_password(passWord: str, hashed: str) -> bool:
    """Extract salt từ hashed, hash lại passWord, so sánh constant-time."""
    return pwd_context.verify(passWord, hashed)


# ── JWT ──────────────────────────────────────────────────────────────────────

def create_access_token(user_id: str, role_name: str) -> str:
    """
    Payload nhúng role_name để RBAC check không cần query DB.
    exp tự động được jose kiểm tra khi decode.
    """
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub":  user_id,    # subject — ID của user
        "role": role_name,  # nhúng role để deps.py dùng trực tiếp
        "type": "access",   # phân biệt với refresh token
        "exp":  expire,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    """
    Refresh token chỉ chứa sub + type — không nhúng role.
    Role có thể thay đổi, refresh token tồn tại lâu → tránh stale data.
    """
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    payload = {
        "sub":  user_id,
        "type": "refresh",
        "exp":  expire,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict: # giải mã token và trả về payload
    """
    Raises JWTError nếu:
    - Sai chữ ký
    - Hết hạn (exp < now)
    - Malformed (không parse được)
    """
    return jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],  # list — tránh algorithm confusion attack
    )