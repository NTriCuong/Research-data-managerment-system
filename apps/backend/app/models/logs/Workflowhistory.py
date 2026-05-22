import uuid
from datetime import datetime

from sqlalchemy import TIMESTAMP, CheckConstraint, ForeignKey, String, Text, text
from sqlalchemy.dialects.postgresql import INET, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.config import Base
from app.models.enum import WorkflowStatus, WorkflowStatusType


class WorkflowHistory(Base):
    __tablename__ = "workflow_history"
    __table_args__ = (
        CheckConstraint("staging_id IS NOT NULL OR research_id IS NOT NULL", name="ck_workflow_target_required"),
        CheckConstraint(
            "from_status IS NULL OR from_status <> to_status "
            "OR action_code IN ('UPDATE_APPROVED_RECORD', 'CREATE_METADATA_VERSION')",
            name="ck_workflow_status_change",
        ),
        {"schema": "log"},
    )

    workflow_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    staging_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("staging.research_objects.staging_id"), nullable=True)
    research_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("core.research_objects.research_id"), nullable=True)
    from_status: Mapped[WorkflowStatus | None] = mapped_column(WorkflowStatusType, nullable=True)
    to_status: Mapped[WorkflowStatus] = mapped_column(WorkflowStatusType, nullable=False)
    action_code: Mapped[str] = mapped_column(String(100), nullable=False)
    action_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    performed_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("auth.users.user_id"), nullable=False)
    performed_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default="now()")
    ip_address: Mapped[str | None] = mapped_column(INET, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)