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
        # Partial index — chỉ index user đang active, nhỏ hơn full index
        Index("idx_users_active_email", "email", postgresql_where="is_deleted = FALSE"),
        Index("idx_users_role", "role_id",       postgresql_where="is_deleted = FALSE"),
        {"schema": "public"},
    )

    # PK  | id                 | VARCHAR(36)
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    # N,U | email              | VARCHAR(255)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    # N   | hashed_password    | VARCHAR(255)
    # Lưu bcrypt hash — KHÔNG BAO GIỜ lưu plain text
    # bcrypt tự chứa salt nên không cần cột salt riêng
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # N   | full_name          | VARCHAR(255)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # N,U | user_code          | VARCHAR(15) — mã định danh nội bộ (giữ từ ERD gốc)
    user_code: Mapped[str] = mapped_column(String(15), unique=True, nullable=False)

    # FK  | role_id            | SMALLINT → public.roles.id
    role_id: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("public.roles.id"), nullable=False
    )

    # FK  | department_id      | SMALLINT → public.departments.id
    department_id: Mapped[Optional[int]] = mapped_column(
        SmallInteger, ForeignKey("public.departments.id"), nullable=True
    )

    # N   | is_active          | BOOLEAN
    # Rõ nghĩa hơn status SMALLINT
    # False = tài khoản bị vô hiệu hóa bởi admin (khác với soft delete)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # N   | failed_login_count | INT
    # Đếm số lần login sai liên tiếp.
    # Reset về 0 khi login thành công.
    # Khi đạt ngưỡng (VD 5 lần) → set locked_until
    failed_login_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # N   | locked_until       | TIMESTAMPTZ
    # NULL  = tài khoản không bị lock
    # Có giá trị = bị lock tạm thời đến thời điểm này
    # App check: if locked_until and locked_until > now() → từ chối login
    locked_until: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # N   | last_login_at      | TIMESTAMPTZ — thời điểm login thành công gần nhất
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # N   | created_at         | TIMESTAMPTZ
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # N   | updated_at         | TIMESTAMPTZ
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        server_default=func.now(), onupdate=func.now()
    )

    # ── Soft delete ──────────────────────────────────────────────────────────
    # Không xóa user thật — FK từ audit_logs, stg_projects vẫn resolve được.
    # Phân biệt với is_active:
    #   is_active=False → admin tạm khóa, có thể mở lại
    #   is_deleted=True → đã xóa hẳn, không thể login

    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Thời điểm xóa — NULL = chưa xóa
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Admin đã thực hiện xóa user này
    deleted_by: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("public.users.id"), nullable=True
    )

    # relationships
    role           = relationship("Role",         back_populates="users")
    department     = relationship("Department",   back_populates="users")
    refresh_tokens = relationship("RefreshToken", back_populates="user",
                                  cascade="all, delete-orphan")
    audit_logs     = relationship("AuditLog",     back_populates="user")
    login_logs     = relationship("LoginLog",     back_populates="user")
    stg_projects   = relationship("StgProject",   back_populates="owner",
                                  foreign_keys="StgProject.owner_id")