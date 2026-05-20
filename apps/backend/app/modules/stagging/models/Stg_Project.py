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
    Bảng trung tâm của staging schema.
    Lưu toàn bộ vòng đời nháp của một nghiên cứu:
      draft → submitted → under_review → approved/rejected

    DC fields (Dublin Core 15 fields) được nhúng thẳng vào bảng này
    thay vì tách ra bảng research_metadata riêng.
    Lý do: DC fields luôn đi cùng nhau, nhúng inline giảm JOIN,
    đơn giản hóa approved_snapshot và full-text search.
    """
    __tablename__ = "stg_projects"
    __table_args__ = (
        # Chỉ index record chưa bị xóa → partial index nhỏ hơn, nhanh hơn
        Index("idx_stg_owner",      "owner_id", postgresql_where="is_deleted = FALSE"),
        Index("idx_stg_status",     "status",   postgresql_where="is_deleted = FALSE"),
        Index("idx_stg_identifier", "identifier"),
        # GIN index cho full-text search
        Index("idx_stg_fts", "search_vector", postgresql_using="gin"),
        # Constraint: nếu is_deleted=True thì deleted_at phải có giá trị
        CheckConstraint(
            "is_deleted = FALSE OR deleted_at IS NOT NULL",
            name="chk_stg_deleted_at"
        ),
        # Constraint: nếu status != 1 (draft) thì submitted_at phải có giá trị
        CheckConstraint(
            "status = 1 OR submitted_at IS NOT NULL",
            name="chk_stg_submitted_at"
        ),
        {"schema": "staging"},
    )

    # PK  | id              | VARCHAR(36)
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    # N,U | identifier      | VARCHAR(30)
    # Mã định danh duy nhất, dễ đọc. VD: NCKH-2024-0001
    # Dùng để reference giữa staging và core mà không cần UUID dài
    identifier: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)

    # FK  | owner_id        | VARCHAR(36) → public.users.id
    # Researcher đã tạo research này
    owner_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("public.users.id"), nullable=False
    )

    # N   | status          | SMALLINT
    # 1=draft 2=submitted 3=under_review 4=approved 5=rejected
    status: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)

    # ── Dublin Core 15 fields ─────────────────────────────────────────────────
    # Nhúng inline thay vì tách bảng research_metadata
    # dc_subject và dc_contributor lưu dạng JSON array string
    # VD dc_subject: '["machine learning", "computer vision"]'

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

    # N   | version_number  | INT
    # Bắt đầu từ 1, tăng mỗi lần researcher resubmit sau khi bị reject
    # Giúp reviewer biết đây là lần nộp thứ mấy
    version_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # N   | core_project_id | VARCHAR(36)
    # NULL = chưa approve | có giá trị = đã approve và tạo bản core tương ứng
    # Soft reference — không dùng FK cứng vì có thể 2 schema riêng biệt
    core_project_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)

    # N   | submitted_at    | TIMESTAMPTZ — thời điểm submit lần đầu
    submitted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # N   | created_at      | TIMESTAMPTZ
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # N   | updated_at      | TIMESTAMPTZ — tự cập nhật khi có thay đổi
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        server_default=func.now(), onupdate=func.now()
    )

    # ── Soft delete ──────────────────────────────────────────────────────────
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # NULL = chưa xóa
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # VARCHAR(36) thay vì FK để tránh vòng tròn FK phức tạp
    deleted_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)

    # ── Full-text Search ─────────────────────────────────────────────────────
    # TSVECTOR được app cập nhật mỗi khi dc_title/dc_creator/dc_description thay đổi.
    # Query: WHERE search_vector @@ plainto_tsquery('simple', :keyword)
    # Index GIN bên trên giúp query này cực nhanh.
    search_vector: Mapped[Optional[str]] = mapped_column(TSVECTOR, nullable=True)

    # relationships
    owner         = relationship("User",             foreign_keys=[owner_id],
                                 back_populates="stg_projects")
    files         = relationship("StgFile",          back_populates="project",
                                 cascade="all, delete-orphan")
    reviews       = relationship("StgReview",        back_populates="project")
    field_comments = relationship("StgFieldComment", back_populates="project")
    research_authors = relationship("StgResearchAuthor", back_populates="project")
    keywords      = relationship("StgKeyword",       back_populates="project",
                                 cascade="all, delete-orphan")