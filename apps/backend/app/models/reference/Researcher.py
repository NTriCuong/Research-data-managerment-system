import uuid
from datetime import datetime

from sqlalchemy import TIMESTAMP, Boolean, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.config import Base


class Researcher(Base):
    __tablename__ = "researchers"
    __table_args__ = {"schema": "reference"}

    researcher_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)
    orcid: Mapped[str | None] = mapped_column(String(50), nullable=True)
    department_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("reference.departments.department_id"), nullable=True)
    academic_title: Mapped[str | None] = mapped_column(String(100), nullable=True)
    researcher_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_internal: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default="now()")
    updated_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)

    department: Mapped["Department | None"] = relationship("Department", back_populates="researchers")  # noqa: F821