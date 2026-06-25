import uuid
from sqlalchemy import String, Text, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database.base import Base


class UserDevice(Base):
    __tablename__ = "user_devices"
    __table_args__ = {"schema": "notification"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.users.user_id"),
        nullable=False,
        index=True
    )

    fcm_token: Mapped[str] = mapped_column(Text, nullable=False, unique=True)

    device_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    user = relationship(
        "User",
        back_populates="devices"
    )