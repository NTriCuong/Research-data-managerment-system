import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger, Boolean, CheckConstraint, DateTime,
    ForeignKey, Index, String, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.config import Base


class StgFile(Base):
    __tablename__ = "stg_files"
    __table_args__ = (
        Index("idx_stg_files_project", "project_id", postgresql_where="is_deleted = FALSE"),
        CheckConstraint("file_size > 0", name="chk_stg_file_size_positive"),
        CheckConstraint(
            "is_deleted = FALSE OR deleted_at IS NOT NULL",
            name="chk_stg_file_deleted_at"
        ),
        {"schema": "staging"},
    )

    # PK | id            | VARCHAR(36)
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    # FK | project_id    | VARCHAR(36) → staging.stg_projects.id
    # RESTRICT: không cho xóa project nếu còn file
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("staging.stg_projects.id", ondelete="RESTRICT"),
        nullable=False
    )

    # N  | original_name | VARCHAR(500) — tên file gốc người dùng upload
    original_name: Mapped[str] = mapped_column(String(500), nullable=False)

    # N  | stored_name   | VARCHAR(500) — tên file trên object storage (UUID-based)
    # UNIQUE: tránh conflict trên storage
    stored_name: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)

    # N  | file_path     | VARCHAR(1000) — đường dẫn đầy đủ trên object storage
    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)

    # N  | file_size     | BIGINT — bytes (BIGINT vì file có thể > 2GB)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)

    # N  | mime_type     | VARCHAR(127) — VD: application/pdf, image/png
    mime_type: Mapped[str] = mapped_column(String(127), nullable=False)

    # FK | uploaded_by   | VARCHAR(36) → public.users.id
    uploaded_by: Mapped[str] = mapped_column(
        String(36), ForeignKey("public.users.id"), nullable=False
    )

    # N  | created_at    | TIMESTAMPTZ
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # ── Soft delete ──────────────────────────────────────────────────────────
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # relationships
    project  = relationship("StgProject", back_populates="files")
    uploader = relationship("User", foreign_keys=[uploaded_by])