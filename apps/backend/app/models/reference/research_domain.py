import uuid
from datetime import datetime

from sqlalchemy import TIMESTAMP, Boolean, ForeignKey, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class ResearchDomain(Base):
    __tablename__ = "research_domains"
    __table_args__ = {"schema": "reference"}

    domain_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    domain_code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    domain_name: Mapped[str] = mapped_column(String(255), nullable=False)
    parent_domain_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("reference.research_domains.domain_id"), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default="now()")
    updated_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)

    parent: Mapped["ResearchDomain | None"] = relationship("ResearchDomain", remote_side="ResearchDomain.domain_id", back_populates="children")
    children: Mapped[list["ResearchDomain"]] = relationship("ResearchDomain", back_populates="parent")