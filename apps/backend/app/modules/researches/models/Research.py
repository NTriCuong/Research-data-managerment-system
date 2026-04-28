from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, SmallInteger, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.config import Base


class Research(Base):
    __tablename__ = "researches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    research_code: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)

    title: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    abstract: Mapped[str] = mapped_column(Text, nullable=False)
    publication_date: Mapped[date] = mapped_column(Date, nullable=False)

    status: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    created_at: Mapped[date] = mapped_column(Date, nullable=False)
    version: Mapped[str] = mapped_column(String(3), nullable=False)

    department_id: Mapped[int] = mapped_column(
        SmallInteger,
        ForeignKey("departments.id"),
        nullable=False,
    )

    # Python không được đặt tên là metadata vì SQLAlchemy giữ tên này
    # DB vẫn tạo cột tên là metadata, kiểu JSONB
    metadata_data: Mapped[dict] = mapped_column(
        "metadata",
        JSONB,
        nullable=False,
        default=dict,
    )

    department = relationship("Department", back_populates="researches")
    files = relationship("File", back_populates="research")
    keywords = relationship("Keyword", back_populates="research")
    research_authors = relationship("ResearchAuthor", back_populates="research")