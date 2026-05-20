import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    CheckConstraint, DateTime, ForeignKey,
    Index, Integer, SmallInteger, String, Text, func,
)
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.config import Base


class CoreProject(Base):
    """
    Bảng trung tâm core schema — bản chính thức đã được approve.

    Nguyên tắc bất biến:
    - approved_snapshot KHÔNG BAO GIỜ bị UPDATE sau khi tạo
      (bảo vệ bằng PostgreSQL trigger trong migration script)
    - Chỉ Admin được sửa dc_* fields hiện tại
    - Mọi thay đổi PHẢI ghi vào core_edit_logs kèm reason
    """
    __tablename__ = "core_projects"
    __table_args__ = (
        Index("idx_core_stg_id",      "stg_project_id"),
        Index("idx_core_status",      "status"),
        Index("idx_core_approved_at", "approved_at"),
        # Partial index — chỉ index published records cho ES sync
        Index("idx_core_fts",         "search_vector",
              postgresql_using="gin", postgresql_where="status = 1"),
        # GIN index cho approved_snapshot — Admin query diff nhanh
        Index("idx_core_snapshot",    "approved_snapshot", postgresql_using="gin"),
        # last_edited_at phải có giá trị nếu edit_count > 0
        CheckConstraint(
            "edit_count = 0 OR last_edited_at IS NOT NULL",
            name="chk_core_edit_tracking"
        ),
        {"schema": "core"},
    )

    # PK  | id               | VARCHAR(36)
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    # N   | stg_project_id   | VARCHAR(36)
    # Soft reference về staging — KHÔNG dùng FK cứng
    # (staging và core có thể tách thành 2 DB riêng trong tương lai)
    stg_project_id: Mapped[str] = mapped_column(String(36), nullable=False)

    # N   | stg_version_number | INT — version của staging lúc approve
    stg_version_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # N,U | identifier       | VARCHAR(30) — giống identifier trong staging
    identifier: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)

    # ── Immutable Snapshot ───────────────────────────────────────────────────
    # Toàn bộ DC fields tại thời điểm approve — KHÔNG BAO GIỜ UPDATE.
    # Bảo vệ bằng trigger PostgreSQL (xem migration).
    # Admin dashboard dùng để so sánh với DC fields hiện tại (drift detection).
    # VD: {"dc_title": "...", "dc_creator": "...", ...}
    approved_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)

    # ── Dublin Core fields hiện tại ─────────────────────────────────────────
    # Admin có thể sửa → phải ghi vào core_edit_logs kèm reason
    dc_title:       Mapped[str]           = mapped_column(String(500), nullable=False)
    dc_creator:     Mapped[str]           = mapped_column(String(500), nullable=False)
    dc_description: Mapped[Optional[str]] = mapped_column(Text,        nullable=True)
    dc_date:        Mapped[Optional[str]] = mapped_column(String(20),  nullable=True)
    dc_type:        Mapped[int]           = mapped_column(SmallInteger, nullable=False, default=1)
    dc_language:    Mapped[int]           = mapped_column(SmallInteger, nullable=False, default=1)
    dc_publisher:   Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    dc_contributor: Mapped[Optional[str]] = mapped_column(Text,        nullable=True)
    dc_subject:     Mapped[Optional[str]] = mapped_column(Text,        nullable=True)
    dc_relation:    Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    dc_coverage:    Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    dc_rights:      Mapped[int]           = mapped_column(SmallInteger, nullable=False, default=1)
    dc_source:      Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    dc_format:      Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # N   | status           | SMALLINT
    # 1=approved (chưa publish) 2=published 3=retracted 4=hidden
    status: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)

    # FK  | approved_by      | VARCHAR(36) → public.users.id (admin đã duyệt)
    approved_by: Mapped[str] = mapped_column(
        String(36), ForeignKey("public.users.id"), nullable=False
    )

    # N   | approved_at      | TIMESTAMPTZ
    approved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # ── Admin edit tracking ──────────────────────────────────────────────────
    # Tổng quan — chi tiết từng lần sửa xem ở core_edit_logs

    # Admin sửa lần cuối
    last_edited_by: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("public.users.id"), nullable=True
    )
    # Thời điểm sửa lần cuối
    last_edited_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    # Tổng số lần admin đã sửa — tăng mỗi lần UPDATE dc_* field
    edit_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # N   | created_at       | TIMESTAMPTZ
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # N   | updated_at       | TIMESTAMPTZ
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        server_default=func.now(), onupdate=func.now()
    )

    # ── Full-text Search ─────────────────────────────────────────────────────
    # Backup cho Elasticsearch — dùng khi ES chưa sync kịp
    # Chỉ index status=2 (published), xem GIN partial index bên trên
    search_vector: Mapped[Optional[str]] = mapped_column(TSVECTOR, nullable=True)

    # relationships
    approver       = relationship("User", foreign_keys=[approved_by])
    last_editor    = relationship("User", foreign_keys=[last_edited_by])
    files          = relationship("CoreFile",     back_populates="project")
    edit_logs      = relationship("CoreEditLog",  back_populates="project")
    keywords       = relationship("CoreKeyword",  back_populates="project",
                                  cascade="all, delete-orphan")
    research_authors = relationship("CoreResearchAuthor", back_populates="project")
    citations      = relationship("CoreCitation",
                                  foreign_keys="CoreCitation.project_id",
                                  back_populates="project")