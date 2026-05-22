from sqlalchemy import SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.config import Base


class Role(Base):
    __tablename__ = "roles"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)

    users = relationship("User", back_populates="role")