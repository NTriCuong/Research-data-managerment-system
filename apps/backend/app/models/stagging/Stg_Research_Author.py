from sqlalchemy import ForeignKey, Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.config import Base


class StgResearchAuthor(Base):
    """
    Junction table: StgProject ←→ Author.
    Lưu thêm 'role' của author trong research cụ thể đó.
    """
    __tablename__ = "stg_research_authors"
    __table_args__ = {"schema": "staging"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("staging.stg_projects.id", ondelete="RESTRICT"),
        nullable=False
    )

    author_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("public.authors.id"), nullable=False
    )

    # N    | role        | SMALLINT
    # 1=main_author (chủ nhiệm đề tài)
    # 2=co_author (đồng tác giả)
    # 3=supervisor (giáo viên hướng dẫn)
    # 4=contributor (người đóng góp)
    role: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=2)

    project = relationship("StgProject", back_populates="research_authors")
    author  = relationship("Author",     back_populates="research_authors")