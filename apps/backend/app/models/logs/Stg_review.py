import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Index, SmallInteger, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.config import Base


class StgReview(Base):
    """
    Mỗi lần reviewer action → 1 record mới (append-only, không UPDATE).
    action (SMALLINT):
      1=approve  2=reject  3=request_revision  4=comment
    """
    __tablename__ = "stg_reviews"
    __table_args__ = (
        Index("idx_stg_reviews_project",  "project_id"),
        Index("idx_stg_reviews_reviewer", "reviewer_id"),
        {"schema": "staging"},
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("staging.stg_projects.id", ondelete="RESTRICT"),
        nullable=False
    )

    reviewer_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("public.users.id"), nullable=False
    )

    action: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    changed_fields: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    project  = relationship("StgProject", back_populates="reviews")
    reviewer = relationship("User", foreign_keys=[reviewer_id])