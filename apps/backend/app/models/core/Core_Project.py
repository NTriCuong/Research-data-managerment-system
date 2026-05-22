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

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    stg_project_id: Mapped[str] = mapped_column(String(36), nullable=False)

    stg_version_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    identifier: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)

    approved_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)

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

    status: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)

    approved_by: Mapped[str] = mapped_column(
        String(36), ForeignKey("public.users.id"), nullable=False
    )

    approved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    last_edited_by: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("public.users.id"), nullable=True
    )

    last_edited_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    edit_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        server_default=func.now(), onupdate=func.now()
    )


    search_vector: Mapped[Optional[str]] = mapped_column(TSVECTOR, nullable=True)

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