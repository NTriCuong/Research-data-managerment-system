import enum as py_enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import TEXT, DateTime, Enum, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import INET, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.config import Base


class AuditActionEnum(str, py_enum.Enum):
    CREATE           = "CREATE"
    UPDATE           = "UPDATE"
    DELETE           = "DELETE"
    APPROVE          = "APPROVE"
    REJECT           = "REJECT"
    REVOKE           = "REVOKE"
    SUBMIT           = "SUBMIT"
    REQUEST_REVISION = "REQUEST_REVISION"
    PUBLISH          = "PUBLISH"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    # PK   | id           | VARCHAR(36)
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    # FK,N | user_id      | VARCHAR(36) → users.id
    user_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )

    # N    | table_name   | VARCHAR(100)
    table_name: Mapped[str] = mapped_column(String(100), nullable=False)

    # N    | record_id    | UUID
    record_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False), nullable=True
    )

    # N    | action_type  | audit_action ENUM
    action_type: Mapped[AuditActionEnum] = mapped_column(
        Enum(AuditActionEnum, name="audit_action"), nullable=False
    )

    # N    | before_data  | JSONB
    before_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # N    | after_data   | JSONB
    after_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # N    | ip_address   | INET
    ip_address: Mapped[Optional[str]] = mapped_column(INET, nullable=True)

    # N    | user_agent   | TEXT
    user_agent: Mapped[Optional[str]] = mapped_column(TEXT, nullable=True)

    # N    | extra_context| JSONB
    extra_context: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # N    | created_at   | TIMESTAMPTZ
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    user = relationship("User", back_populates="audit_logs")