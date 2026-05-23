import uuid
from datetime import datetime

from sqlalchemy import TIMESTAMP, ForeignKey, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.config import Base
from app.models.enum import UserStatus, UserStatusType
from app.models.auth.refresh_token import RefreshToken  # noqa: F401
from app.models.auth.role import Role  # noqa: F401
from app.models.reference.department import Department  # noqa: F401


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "auth"}

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("auth.roles.role_id"), nullable=False)
    department_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("reference.departments.department_id"), nullable=True)
    status: Mapped[UserStatus] = mapped_column(UserStatusType, nullable=False, server_default="active")
    last_login_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default="now()")
    updated_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)

    role: Mapped["Role"] = relationship("Role", back_populates="users")  # noqa: F821
    department: Mapped["Department | None"] = relationship("Department", back_populates="users")  # noqa: F821
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")  # noqa: F821