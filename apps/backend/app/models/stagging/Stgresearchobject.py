import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import TIMESTAMP, CheckConstraint, Date, ForeignKey, Integer, Numeric, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.config import Base
from app.models.enum import AccessLevel, AccessLevelType, WorkflowStatus, WorkflowStatusType


class StgResearchObject(Base):
    __tablename__ = "research_objects"
    __table_args__ = (
        CheckConstraint("year BETWEEN 1900 AND 2100", name="ck_stg_year_range"),
        {"schema": "staging"},
    )

    staging_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    abstract: Mapped[str | None] = mapped_column(Text, nullable=True)
    output_type_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("reference.output_types.output_type_id"), nullable=False)
    department_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("reference.departments.department_id"), nullable=False)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    date_issued: Mapped[date | None] = mapped_column(Date, nullable=True)
    publisher: Mapped[str | None] = mapped_column(String(255), nullable=True)
    language: Mapped[str | None] = mapped_column(String(50), nullable=True, server_default="vi")
    identifier: Mapped[str | None] = mapped_column(String(255), nullable=True)
    external_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str | None] = mapped_column(Text, nullable=True)
    relation: Mapped[str | None] = mapped_column(Text, nullable=True)
    coverage: Mapped[str | None] = mapped_column(Text, nullable=True)
    rights: Mapped[str | None] = mapped_column(Text, nullable=True)
    access_level: Mapped[AccessLevel] = mapped_column(AccessLevelType, nullable=False, server_default="internal")
    workflow_status: Mapped[WorkflowStatus] = mapped_column(WorkflowStatusType, nullable=False, server_default="draft")
    source_core_research_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("core.research_objects.research_id"), nullable=True)
    update_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_quality_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True, server_default="0")
    metadata_quality_detail: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("auth.users.user_id"), nullable=False)
    submitted_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("auth.users.user_id"), nullable=True)
    submitted_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    reviewed_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("auth.users.user_id"), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    approved_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("auth.users.user_id"), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    revision_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default="now()")
    updated_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)

    output_type: Mapped["OutputType"] = relationship("OutputType")  # noqa: F821
    department: Mapped["Department"] = relationship("Department")   # noqa: F821
    authors: Mapped[list["StgResearchObjectAuthor"]] = relationship("StgResearchObjectAuthor", back_populates="research_object", cascade="all, delete-orphan")
    domains: Mapped[list["StgResearchObjectDomain"]] = relationship("StgResearchObjectDomain", back_populates="research_object", cascade="all, delete-orphan")
    keywords: Mapped[list["StgResearchObjectKeyword"]] = relationship("StgResearchObjectKeyword", back_populates="research_object", cascade="all, delete-orphan")
    file_attachments: Mapped[list["StgFileAttachment"]] = relationship("StgFileAttachment", back_populates="research_object", cascade="all, delete-orphan")