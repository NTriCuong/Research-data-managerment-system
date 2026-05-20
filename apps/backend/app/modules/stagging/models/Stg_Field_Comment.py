import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.config import Base

# Tuple dùng cho CheckConstraint — chỉ cho phép comment vào DC fields hợp lệ
_VALID_DC_FIELDS = (
    'dc_title', 'dc_creator', 'dc_description', 'dc_date',
    'dc_type', 'dc_language', 'dc_publisher', 'dc_contributor',
    'dc_subject', 'dc_relation', 'dc_coverage', 'dc_rights',
    'dc_source', 'dc_format',
)


class StgFieldComment(Base):
    """
    Reviewer annotate vào từng field Dublin Core cụ thể.

    Khác với StgReview (nhận xét tổng thể),
    StgFieldComment chỉ rõ field nào cần sửa và tại sao.

    Researcher biết chính xác cần sửa field nào →
    mark is_resolved=True sau khi sửa xong.
    """
    __tablename__ = "stg_field_comments"
    __table_args__ = (
        CheckConstraint(
            f"field_name IN {_VALID_DC_FIELDS}",
            name="chk_stg_field_name_valid"
        ),
        # Nếu is_resolved=True thì phải có resolved_at
        CheckConstraint(
            "is_resolved = FALSE OR resolved_at IS NOT NULL",
            name="chk_stg_field_comment_resolved"
        ),
        {"schema": "staging"},
    )

    # PK | id          | VARCHAR(36)
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    # FK | project_id  | VARCHAR(36) → staging.stg_projects.id
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("staging.stg_projects.id", ondelete="RESTRICT"),
        nullable=False
    )

    # FK | reviewer_id | VARCHAR(36) → public.users.id
    reviewer_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("public.users.id"), nullable=False
    )

    # N  | field_name  | VARCHAR(50) — tên DC field bị comment
    field_name: Mapped[str] = mapped_column(String(50), nullable=False)

    # N  | comment     | TEXT — nội dung góp ý
    comment: Mapped[str] = mapped_column(Text, nullable=False)

    # N  | is_resolved | BOOLEAN — False=chưa xử lý, True=researcher đã sửa
    is_resolved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # N  | resolved_at | TIMESTAMPTZ — thời điểm mark resolved
    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # N  | created_at  | TIMESTAMPTZ
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # relationships
    project  = relationship("StgProject", back_populates="field_comments")
    reviewer = relationship("User", foreign_keys=[reviewer_id])