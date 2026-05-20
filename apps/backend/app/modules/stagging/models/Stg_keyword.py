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

    # PK | id         | VARCHAR(36)
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    # FK | project_id | VARCHAR(36) → staging.stg_projects.id
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("staging.stg_projects.id", ondelete="CASCADE"),
        nullable=False
    )

    # N  | keyword    | VARCHAR(100)
    keyword: Mapped[str] = mapped_column(String(100), nullable=False)

    # N  | language   | SMALLINT — 1=vi 2=en
    language: Mapped[int] = mapped_column(nullable=False, default=1)

    # relationship
    project = relationship("StgProject", back_populates="keywords")