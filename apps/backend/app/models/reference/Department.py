import uuid
from datetime import datetime

from sqlalchemy import TIMESTAMP, Boolean, ForeignKey, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.config import Base


class Department(Base):
    __tablename__ = "departments"
    __table_args__ = {"schema": "reference"}

    department_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    department_code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    department_name: Mapped[str] = mapped_column(String(255), nullable=False)
    parent_department_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("reference.departments.department_id"), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default="now()")
    updated_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)

    parent: Mapped["Department | None"] = relationship("Department", remote_side="Department.department_id", back_populates="children")
    children: Mapped[list["Department"]] = relationship("Department", back_populates="parent")
    researchers: Mapped[list["Researcher"]] = relationship("Researcher", back_populates="department")  # noqa: F821
    users: Mapped[list["User"]] = relationship("User", back_populates="department")  # noqa: F821