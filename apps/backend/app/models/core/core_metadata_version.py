import uuid
from datetime import datetime

from sqlalchemy import TIMESTAMP, ForeignKey, Integer, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.config import Base
from app.models.core.core_research_object import CoreResearchObject  # noqa: F401


class CoreMetadataVersion(Base):
    __tablename__ = "metadata_versions"
    __table_args__ = (
        UniqueConstraint("research_id", "version_no", name="uq_metadata_version"),
        {"schema": "core"},
    )

    version_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    research_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("core.research_objects.research_id", ondelete="CASCADE"), nullable=False)
    version_no: Mapped[int] = mapped_column(Integer, nullable=False)
    metadata_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)
    change_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("auth.users.user_id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default="now()")

    research_object: Mapped["CoreResearchObject"] = relationship("CoreResearchObject", back_populates="metadata_versions")  # noqa: F821