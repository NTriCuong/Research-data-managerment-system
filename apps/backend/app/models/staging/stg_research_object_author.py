import uuid
from datetime import datetime

from sqlalchemy import TIMESTAMP, ForeignKey, Integer, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.enum import AuthorRole, AuthorRoleType

class StgResearchObjectAuthor(Base):
    __tablename__ = "research_object_authors"
    __table_args__ = (
        UniqueConstraint("staging_id", "author_order", name="uq_staging_author_order"),
        {"schema": "staging"},
    )

    staging_author_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    staging_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("staging.research_objects.staging_id", ondelete="CASCADE"), nullable=False)
    researcher_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("reference.researchers.researcher_id"), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    affiliation: Mapped[str | None] = mapped_column(String(255), nullable=True)
    author_order: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    author_role: Mapped[AuthorRole] = mapped_column(AuthorRoleType, nullable=False, server_default="creator")
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default="now()")

    research_object: Mapped["StgResearchObject"] = relationship("StgResearchObject", back_populates="authors")  # noqa: F821
    researcher: Mapped["Researcher | None"] = relationship("Researcher")  # noqa: F821