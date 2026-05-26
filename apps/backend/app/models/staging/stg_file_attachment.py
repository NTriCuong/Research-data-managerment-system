import uuid
from datetime import datetime

from sqlalchemy import TIMESTAMP, BigInteger, CheckConstraint, ForeignKey, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.config import Base
from app.models.enum import AccessLevel, AccessLevelType, FileStatus, FileStatusType

class StgFileAttachment(Base):
    __tablename__ = "file_attachments"
    __table_args__ = (
        CheckConstraint("file_size_bytes > 0", name="ck_stg_file_size_positive"),
        {"schema": "staging"},
    )

    file_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    staging_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("staging.research_objects.staging_id", ondelete="CASCADE"), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_extension: Mapped[str | None] = mapped_column(String(20), nullable=True)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    checksum_sha256: Mapped[str | None] = mapped_column(String(128), nullable=True)
    file_status: Mapped[FileStatus] = mapped_column(FileStatusType, nullable=False, server_default="active")
    uploaded_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("auth.users.user_id"), nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default="now()")
    access_level: Mapped[AccessLevel] = mapped_column(AccessLevelType, nullable=False, server_default="internal")

    research_object: Mapped["StgResearchObject"] = relationship("StgResearchObject", back_populates="file_attachments")  # noqa: F821