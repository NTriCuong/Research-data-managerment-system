import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    Boolean, Date, DateTime, ForeignKey,
    Index, Integer, SmallInteger, String, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.config import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        Index("idx_users_active_email", "email", postgresql_where="is_deleted = FALSE"),
        Index("idx_users_role", "role_id",       postgresql_where="is_deleted = FALSE"),
        {"schema": "public"},
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    full_name: Mapped[str] = mapped_column(String(255), nullable=False)

    user_code: Mapped[str] = mapped_column(String(15), unique=True, nullable=False)

    role_id: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("public.roles.id"), nullable=False
    )

    department_id: Mapped[Optional[int]] = mapped_column(
        SmallInteger, ForeignKey("public.departments.id"), nullable=True
    )

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    failed_login_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    locked_until: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        server_default=func.now(), onupdate=func.now()
    )

    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    deleted_by: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("public.users.id"), nullable=True
    )

    role           = relationship("Role",         back_populates="users")
    department     = relationship("Department",   back_populates="users")
    refresh_tokens = relationship("RefreshToken", back_populates="user",
                                  cascade="all, delete-orphan")
    audit_logs     = relationship("AuditLog",     back_populates="user")
    login_logs     = relationship("LoginLog",     back_populates="user")
    stg_projects   = relationship("StgProject",   back_populates="owner",
                                  foreign_keys="StgProject.owner_id")