from sqlalchemy import ForeignKey, Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.config import Base


class ResearchAuthor(Base):
    __tablename__ = "research_author"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    research_code: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("researches.research_code"),
        nullable=False,
    )

    author_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("authors.id"),
        nullable=False,
    )

    # 1 giáo viên hướng dẫn, 2 chủ nhiệm đề tài, 3 người đóng góp
    role: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    research = relationship("Research", back_populates="research_authors")
    author = relationship("Author", back_populates="research_authors")