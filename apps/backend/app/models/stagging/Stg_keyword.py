import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.config import Base


class StgKeyword(Base):
    """
    Keyword gắn với từng StgProject (one-many).
    Tách thành bảng riêng thay vì lưu JSON trong dc_subject
    để dễ query, filter, và thống kê theo keyword.
    """
    __tablename__ = "stg_keywords"
    __table_args__ = {"schema": "staging"}

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("staging.stg_projects.id", ondelete="CASCADE"),
        nullable=False
    )

    keyword: Mapped[str] = mapped_column(String(100), nullable=False)

    language: Mapped[int] = mapped_column(nullable=False, default=1)

    project = relationship("StgProject", back_populates="keywords")