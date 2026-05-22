import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import TEXT, Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.config import Base


class LoginLog(Base):
    __tablename__ = "login_logs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    user_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )

    email_attempted: Mapped[str] = mapped_column(String(320), nullable=False)

    success: Mapped[bool] = mapped_column(Boolean, nullable=False)

    failure_reason: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    ip_address: Mapped[Optional[str]] = mapped_column(INET, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    user_agent: Mapped[Optional[str]] = mapped_column(TEXT, nullable=True)

    user = relationship("User", back_populates="login_logs")