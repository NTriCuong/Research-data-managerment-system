from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.config import Base



class Keyword(Base):
    __tablename__ = "keywords"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    key: Mapped[str] = mapped_column(Text, nullable=False)

    research_code: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("researches.research_code"),
        nullable=False,
    )

    research = relationship("Research", back_populates="keywords")