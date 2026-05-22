import uuid
from datetime import datetime

from sqlalchemy import TIMESTAMP, ForeignKey, String, Text, text
from sqlalchemy.dialects.postgresql import INET, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.config import Base


class LoginLog(Base):
    __tablename__ = "login_logs"
    __table_args__ = {"schema": "log"}

    login_log_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("auth.users.user_id"), nullable=True)
    username_attempted: Mapped[str | None] = mapped_column(String(255), nullable=True)
    login_result: Mapped[str] = mapped_column(String(50), nullable=False)
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(INET, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default="now()")