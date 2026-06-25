import uuid
from datetime import datetime

from sqlalchemy import String, Text, ForeignKey, TIMESTAMP, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database.base import Base


class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = {"schema": "notification"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)

    message: Mapped[str] = mapped_column(Text, nullable=False)

    notification_type: Mapped[str] = mapped_column(String(50), nullable=False)

    action_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    sender_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.users.user_id"),
        nullable=True
    )

    research_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("staging.research_objects.staging_id"),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text("now()")
    )

    sender = relationship(
        "User",
        foreign_keys=[sender_user_id]
    )

    research = relationship(
        "StgResearchObject"
    )

    user_notifications: Mapped[list["UserNotification"]] = relationship(
        "UserNotification",
        back_populates="notification",
        cascade="all, delete-orphan"
    )