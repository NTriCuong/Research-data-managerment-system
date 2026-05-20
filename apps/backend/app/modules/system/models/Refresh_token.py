import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.config import Base


class RefreshToken(Base):
    """
    Quản lý JWT refresh token — blacklist pattern.

    Khi nào tạo record:  Login thành công
    Khi nào revoke:      Logout / refresh token / admin force logout
    Kiểm tra hợp lệ:
      WHERE token = :t AND revoked_at IS NULL AND expires_at > NOW()
    """
    __tablename__ = "refresh_tokens"
    __table_args__ = (
        # Partial index — chỉ index token chưa bị revoke
        # Nhỏ hơn full index, blacklist check nhanh hơn
        Index("idx_refresh_tokens_active", "token",
              postgresql_where="revoked_at IS NULL"),
        {"schema": "public"},
    )

    # PK | id         | VARCHAR(36)
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    # FK | user_id    | VARCHAR(36) → public.users.id
    # CASCADE: xóa user → xóa hết token
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("public.users.id", ondelete="CASCADE"), nullable=False
    )

    # N  | token      | TEXT — JWT refresh token string
    token: Mapped[str] = mapped_column(Text, nullable=False, unique=True)

    # N  | expires_at | TIMESTAMPTZ
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    # N  | revoked_at | TIMESTAMPTZ
    # NULL = còn hiệu lực | có giá trị = đã thu hồi
    revoked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # N  | created_at | TIMESTAMPTZ
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    user = relationship("User", back_populates="refresh_tokens")