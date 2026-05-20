from typing import Optional

from sqlalchemy import ForeignKey, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.config import Base


class Author(Base):
    __tablename__ = "authors"
    __table_args__ = {"schema": "public"}

    # PK   | id              | INTEGER
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # N    | full_name       | VARCHAR(50)
    full_name: Mapped[str] = mapped_column(String(50), nullable=False)

    # N,U  | email           | VARCHAR(50)
    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    # N    | author_code     | VARCHAR(12)
    author_code: Mapped[str] = mapped_column(String(12), nullable=False, unique=True)

    # N    | author_type     | SMALLINT
    # 1=student 2=lecturer 3=researcher
    author_type: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    # N    | education_level | SMALLINT
    # 1=undergraduate 2=master 3=doctor 4=professor
    education_level: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    # FK,N | department_id   | SMALLINT → public.departments.id
    department_id: Mapped[Optional[int]] = mapped_column(
        SmallInteger, ForeignKey("public.departments.id"), nullable=True
    )

    # relationships
    department       = relationship("Department",        back_populates="authors")
    research_authors = relationship("StgResearchAuthor", back_populates="author")