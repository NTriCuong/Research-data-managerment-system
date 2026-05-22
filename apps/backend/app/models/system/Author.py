from typing import Optional

from sqlalchemy import ForeignKey, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.config import Base


class Author(Base):
    __tablename__ = "authors"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    full_name: Mapped[str] = mapped_column(String(50), nullable=False)

    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    author_code: Mapped[str] = mapped_column(String(12), nullable=False, unique=True)

    author_type: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    education_level: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    department_id: Mapped[Optional[int]] = mapped_column(
        SmallInteger, ForeignKey("public.departments.id"), nullable=True
    )

    department       = relationship("Department",        back_populates="authors")
    research_authors = relationship("StgResearchAuthor", back_populates="author")