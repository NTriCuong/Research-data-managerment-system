from sqlalchemy import ForeignKey, Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.config import Base


class Author(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    full_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    author_code: Mapped[str] = mapped_column(String(12), unique=True, nullable=False)

    # 1 sinh viên, 2 giảng viên
    author_type: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    # 1 cao đẳng, 2 đại học, 3 cao học, 4 thạc sĩ, 5 tiến sĩ
    education_level: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    department_id: Mapped[int] = mapped_column(
        SmallInteger,
        ForeignKey("departments.id"),
        nullable=False,
    )

    department = relationship("Department", back_populates="authors")
    research_authors = relationship("ResearchAuthor", back_populates="author")