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

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("staging.stg_projects.id", ondelete="RESTRICT"),
        nullable=False
    )

    original_name: Mapped[str] = mapped_column(String(500), nullable=False)

    stored_name: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)

    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)

    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)

    mime_type: Mapped[str] = mapped_column(String(127), nullable=False)

    uploaded_by: Mapped[str] = mapped_column(
        String(36), ForeignKey("public.users.id"), nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    project  = relationship("StgProject", back_populates="files")
    uploader = relationship("User", foreign_keys=[uploaded_by])