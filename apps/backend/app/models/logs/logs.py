import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import INET, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.config import Base


# ============================================================
#  AuditLog  — ghi lại mọi thay đổi dữ liệu quan trọng
# ============================================================

class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = (
        # Composite index: query "toàn bộ log của research X"
        # WHERE entity_type='stg_project' AND entity_id='xxx' → rất nhanh
        Index("idx_audit_entity",     "entity_type", "entity_id"),
        Index("idx_audit_user",       "user_id"),
        Index("idx_audit_created_at", "created_at"),
        {"schema": "log"},
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    user_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("public.users.id", ondelete="SET NULL"), nullable=True
    )

    action: Mapped[str] = mapped_column(String(50), nullable=False)

    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)

    entity_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)

    old_value: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    new_value: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    ip_address: Mapped[Optional[str]] = mapped_column(INET, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    user = relationship("User", back_populates="audit_logs")


class LoginLog(Base):
    __tablename__ = "login_logs"
    __table_args__ = (
        Index("idx_login_user",       "user_id"),
        Index("idx_login_created_at", "created_at"),
        {"schema": "log"},
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    user_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("public.users.id", ondelete="SET NULL"), nullable=True
    )

    email_attempted: Mapped[str] = mapped_column(String(320), nullable=False)

    success: Mapped[bool] = mapped_column(Boolean, nullable=False)

    failure_reason: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    ip_address: Mapped[Optional[str]] = mapped_column(INET, nullable=True)

    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    user = relationship("User", back_populates="login_logs")