from sqlalchemy import Float, ForeignKey, Integer, SmallInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.config import Base


class File(Base):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    research_code: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("researches.research_code"),
        nullable=False,
    )

    file_name: Mapped[str] = mapped_column(String(20), nullable=False)

    # 1 pdf, 2 docx
    file_type: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    file_size: Mapped[float] = mapped_column(Float, nullable=False)

    upload_by: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id"),
        nullable=False,
    )

    file_url: Mapped[str] = mapped_column(Text, nullable=False)

    research = relationship("Research", back_populates="files")
    uploader = relationship("User", back_populates="uploaded_files")