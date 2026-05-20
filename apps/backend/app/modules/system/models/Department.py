from sqlalchemy import SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.config import Base


class Department(Base):
    __tablename__ = "departments"
    __table_args__ = {"schema": "public"}

    # PK | id   | SMALLINT
    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, autoincrement=True)

    # N  | name | VARCHAR(50)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

    # relationships
    users   = relationship("User",   back_populates="department")
    authors = relationship("Author", back_populates="department")