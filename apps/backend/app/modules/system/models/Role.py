from sqlalchemy import SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.config import Base


class Role(Base):
    __tablename__ = "roles"
    __table_args__ = {"schema": "public"}

    # PK  | id   | SMALLINT
    # 1=super_admin 2=security_admin 3=data_entry 4=reviewer 5=approver 6=instructor
    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, autoincrement=True)

    # N,U | name | VARCHAR(20)
    name: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)

    users = relationship("User", back_populates="role")