import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger, Boolean, CheckConstraint, DateTime,
    ForeignKey, Index, Integer, SmallInteger, String, Text,
    UniqueConstraint, func,
)
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.config import Base


# ============================================================
#  CoreFile
# ============================================================

class CoreFile(Base):
    """
    File đính kèm trong core.

    is_snapshot_file=True  → copy từ staging lúc approve (bất biến)
    is_snapshot_file=False → admin upload thêm sau khi publish
    """
    __tablename__ = "core_files"
    __table_args__ = (
        Index("idx_core_files_project",  "project_id"),
        Index("idx_core_files_snapshot", "project_id",
              postgresql_where="is_snapshot_file = TRUE"),
        CheckConstraint("file_size > 0", name="chk_core_file_size"),
        {"schema": "core"},
    )

    # PK | id               | VARCHAR(36)
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    # FK | project_id       | VARCHAR(36) → core.core_projects.id
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("core.core_projects.id", ondelete="RESTRICT"),
        nullable=False
    )

    original_name: Mapped[str] = mapped_column(String(500), nullable=False)
    stored_name:   Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    file_path:     Mapped[str] = mapped_column(String(1000), nullable=False)
    file_size:     Mapped[int] = mapped_column(BigInteger, nullable=False)
    mime_type:     Mapped[str] = mapped_column(String(127), nullable=False)

    # True=snapshot từ staging (bất biến) | False=admin upload thêm
    is_snapshot_file: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    uploaded_by: Mapped[str] = mapped_column(
        String(36), ForeignKey("public.users.id"), nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    project  = relationship("CoreProject", back_populates="files")
    uploader = relationship("User", foreign_keys=[uploaded_by])


# ============================================================
#  CoreResearchAuthor
# ============================================================

class CoreResearchAuthor(Base):
    """Junction table: CoreProject ←→ Author (mirror của StgResearchAuthor)."""
    __tablename__ = "core_research_authors"
    __table_args__ = {"schema": "core"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("core.core_projects.id", ondelete="RESTRICT"),
        nullable=False
    )

    author_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("public.authors.id"), nullable=False
    )

    # 1=main_author 2=co_author 3=supervisor 4=contributor
    role: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=2)

    project = relationship("CoreProject", back_populates="research_authors")
    author  = relationship("Author")


# ============================================================
#  CoreKeyword
# ============================================================

class CoreKeyword(Base):
    """Keyword của core project — mirror của StgKeyword."""
    __tablename__ = "core_keywords"
    __table_args__ = {"schema": "core"}

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("core.core_projects.id", ondelete="CASCADE"),
        nullable=False
    )

    keyword: Mapped[str] = mapped_column(String(100), nullable=False)

    # 1=vi 2=en
    language: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)

    project = relationship("CoreProject", back_populates="keywords")


# ============================================================
#  CoreEditLog
# ============================================================

_VALID_EDITABLE_FIELDS = (
    'dc_title', 'dc_creator', 'dc_description', 'dc_date',
    'dc_type', 'dc_language', 'dc_publisher', 'dc_contributor',
    'dc_subject', 'dc_relation', 'dc_coverage', 'dc_rights',
    'dc_source', 'dc_format', 'status',
)


class CoreEditLog(Base):
    """
    Ghi lại mỗi lần admin sửa field trong core_projects.

    Quy tắc:
    - Mỗi field sửa = 1 record riêng (không gộp nhiều field vào 1 record)
    - reason KHÔNG được rỗng — bắt buộc giải thích lý do
    - Append-only — không UPDATE, không DELETE record này
    - ON DELETE RESTRICT — không xóa project nếu còn edit log
    """
    __tablename__ = "core_edit_logs"
    __table_args__ = (
        Index("idx_core_edit_project",  "project_id"),
        Index("idx_core_edit_admin",    "admin_id"),
        Index("idx_core_edit_at",       "edited_at"),
        CheckConstraint(
            f"field_name IN {_VALID_EDITABLE_FIELDS}",
            name="chk_core_edit_field_valid"
        ),
        CheckConstraint(
            "trim(reason) <> ''",
            name="chk_core_edit_reason_not_empty"
        ),
        {"schema": "core"},
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    # FK | project_id | VARCHAR(36) → core.core_projects.id
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("core.core_projects.id", ondelete="RESTRICT"),
        nullable=False
    )

    # FK | admin_id   | VARCHAR(36) → public.users.id
    admin_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("public.users.id"), nullable=False
    )

    # Tên field DC bị sửa
    field_name: Mapped[str] = mapped_column(String(50), nullable=False)

    # Giá trị trước và sau khi sửa (TEXT để lưu mọi kiểu dữ liệu)
    old_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    new_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Lý do sửa — BẮT BUỘC, không được rỗng
    reason: Mapped[str] = mapped_column(Text, nullable=False)

    ip_address: Mapped[Optional[str]] = mapped_column(INET, nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    edited_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    project = relationship("CoreProject", back_populates="edit_logs")
    admin   = relationship("User", foreign_keys=[admin_id])


# ============================================================
#  CoreCitation
# ============================================================

class CoreCitation(Base):
    """
    Quan hệ trích dẫn giữa các core project.

    relation_type (SMALLINT):
      1=cites            A trích dẫn B
      2=is_cited_by      A được B trích dẫn
      3=is_part_of       A là một phần của B
      4=has_part         A chứa B
      5=references       A tham chiếu B
      6=is_referenced_by A được B tham chiếu

    Constraints:
      - Không tự trích dẫn (project_id ≠ cited_project_id)
      - Không trùng lặp cùng chiều (unique 3 cột)
    """
    __tablename__ = "core_citations"
    __table_args__ = (
        UniqueConstraint("project_id", "cited_project_id", "relation_type",
                         name="uq_core_citations"),
        CheckConstraint("project_id <> cited_project_id",
                        name="chk_core_no_self_citation"),
        Index("idx_core_citation_project", "project_id"),
        Index("idx_core_citation_cited",   "cited_project_id"),
        {"schema": "core"},
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("core.core_projects.id", ondelete="RESTRICT"),
        nullable=False
    )

    cited_project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("core.core_projects.id", ondelete="RESTRICT"),
        nullable=False
    )

    # 1=cites 2=is_cited_by 3=is_part_of 4=has_part 5=references 6=is_referenced_by
    relation_type: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    project        = relationship("CoreProject", foreign_keys=[project_id],
                                  back_populates="citations")
    cited_project  = relationship("CoreProject", foreign_keys=[cited_project_id])