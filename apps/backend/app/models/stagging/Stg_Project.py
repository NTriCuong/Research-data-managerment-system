import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean, CheckConstraint, DateTime, ForeignKey,
    Index, Integer, SmallInteger, String, Text, func,
)
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.config import Base


class StgProject(Base):
    """
    draft → submitted → under_review → approved/rejected
    DC fields (Dublin Core 15 fields) 
    """
    __tablename__ = "stg_projects"
    __table_args__ = (
        Index("idx_stg_owner",      "owner_id", postgresql_where="is_deleted = FALSE"),
        Index("idx_stg_status",     "status",   postgresql_where="is_deleted = FALSE"),
        Index("idx_stg_identifier", "identifier"),
        Index("idx_stg_fts", "search_vector", postgresql_using="gin"),
        CheckConstraint(
            "is_deleted = FALSE OR deleted_at IS NOT NULL",
            name="chk_stg_deleted_at"
        ),
        CheckConstraint(
            "status = 1 OR submitted_at IS NOT NULL",
            name="chk_stg_submitted_at"
        ),
        {"schema": "staging"},
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    identifier: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)

    owner_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("public.users.id"), nullable=False
    )

    status: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)

    dc_title:       Mapped[str]            = mapped_column(String(500), nullable=False)
    dc_creator:     Mapped[str]            = mapped_column(String(500), nullable=False)
    dc_description: Mapped[Optional[str]]  = mapped_column(Text,        nullable=True)
    dc_date:        Mapped[Optional[str]]  = mapped_column(String(20),  nullable=True)  # yyyy hoặc yyyy-MM-dd
    dc_type:        Mapped[int]            = mapped_column(SmallInteger, nullable=False, default=1)
    # 1=article 2=thesis 3=conference_paper 4=book 5=book_chapter 6=report 7=dataset 8=other
    dc_language:    Mapped[int]            = mapped_column(SmallInteger, nullable=False, default=1)
    # 1=vi 2=en 3=vi_en
    dc_publisher:   Mapped[Optional[str]]  = mapped_column(String(255), nullable=True)
    dc_contributor: Mapped[Optional[str]]  = mapped_column(Text,        nullable=True)  # JSON array
    dc_subject:     Mapped[Optional[str]]  = mapped_column(Text,        nullable=True)  # JSON array, tối đa 10
    dc_relation:    Mapped[Optional[str]]  = mapped_column(String(500), nullable=True)
    dc_coverage:    Mapped[Optional[str]]  = mapped_column(String(255), nullable=True)
    dc_rights:      Mapped[int]            = mapped_column(SmallInteger, nullable=False, default=1)
    # 1=public 2=restricted 3=private
    dc_source:      Mapped[Optional[str]]  = mapped_column(String(500), nullable=True)
    dc_format:      Mapped[Optional[str]]  = mapped_column(String(100), nullable=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    core_project_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)

    submitted_at: Mapped[Optional[datetime]] = mapped_column(
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

    deleted_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)


    search_vector: Mapped[Optional[str]] = mapped_column(TSVECTOR, nullable=True)


    owner         = relationship("User",             foreign_keys=[owner_id],
                                 back_populates="stg_projects")
    files         = relationship("StgFile",          back_populates="project",
                                 cascade="all, delete-orphan")
    reviews       = relationship("StgReview",        back_populates="project")
    field_comments = relationship("StgFieldComment", back_populates="project")
    research_authors = relationship("StgResearchAuthor", back_populates="project")
    keywords      = relationship("StgKeyword",       back_populates="project",
                                 cascade="all, delete-orphan")