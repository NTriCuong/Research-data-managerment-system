import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Index, SmallInteger, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.config import Base


class StgReview(Base):
    """
    Ghi lại mỗi hành động của reviewer/approver trên một StgProject.

    Mỗi lần reviewer action → 1 record mới (append-only, không UPDATE).
    Lịch sử review đầy đủ → biết ai làm gì, khi nào.

    action (SMALLINT):
      1=approve  2=reject  3=request_revision  4=comment
    """
    __tablename__ = "stg_reviews"
    __table_args__ = (
        Index("idx_stg_reviews_project",  "project_id"),
        Index("idx_stg_reviews_reviewer", "reviewer_id"),
        {"schema": "staging"},
    )

    # PK | id             | VARCHAR(36)
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    # FK | project_id     | VARCHAR(36) → staging.stg_projects.id
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("staging.stg_projects.id", ondelete="RESTRICT"),
        nullable=False
    )

    # FK | reviewer_id    | VARCHAR(36) → public.users.id (reviewer/approver)
    reviewer_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("public.users.id"), nullable=False
    )

    # N  | action         | SMALLINT — 1=approve 2=reject 3=request_revision 4=comment
    action: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    # N  | comment        | TEXT — nhận xét tổng thể của reviewer
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # N  | changed_fields | JSONB
    # Danh sách field cần sửa kèm gợi ý cụ thể.
    # VD: [{"field": "dc_title", "suggestion": "Cần thêm năm nghiên cứu"}]
    changed_fields: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # N  | created_at     | TIMESTAMPTZ
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # relationships
    project  = relationship("StgProject", back_populates="reviews")
    reviewer = relationship("User", foreign_keys=[reviewer_id])