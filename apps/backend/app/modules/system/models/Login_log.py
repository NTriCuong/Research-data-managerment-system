import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import TEXT, Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.config import Base


class LoginLog(Base):
    __tablename__ = "login_logs"

    # PK  | id              | VARCHAR(36) — surrogate key (user có thể login nhiều lần)
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    # N   | user_id         | VARCHAR(36) → users.id  (nullable: login sai email cũng được ghi)
    user_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )

    # N   | email_attempted | VARCHAR(320)
    email_attempted: Mapped[str] = mapped_column(String(320), nullable=False)

    # N   | success         | BOOLEAN
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)

    # N   | failure_reason  | VARCHAR(100)
    failure_reason: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # N   | ip_address      | INET
    ip_address: Mapped[Optional[str]] = mapped_column(INET, nullable=True)

    # N   | created_at      | TIMESTAMPTZ
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # N   | user_agent      | TEXT
    user_agent: Mapped[Optional[str]] = mapped_column(TEXT, nullable=True)

    user = relationship("User", back_populates="login_logs")