import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.config import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(50), nullable=False)
    user_code: Mapped[str] = mapped_column(String(15), unique=True, nullable=False)

    role_id: Mapped[int] = mapped_column(
        SmallInteger,
        ForeignKey("roles.id"),
        nullable=False,
    )

    create_at: Mapped[date] = mapped_column(Date, nullable=False)
    update_at: Mapped[date] = mapped_column(Date, nullable=False)

    # 1 active, 2 inactive
    status: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    role = relationship("Role", back_populates="users")
    uploaded_files = relationship("File", back_populates="uploader")
    activity_logs = relationship("ActivityLog", back_populates="user")