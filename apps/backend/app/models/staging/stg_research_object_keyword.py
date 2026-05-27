import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

class StgResearchObjectKeyword(Base):
    __tablename__ = "research_object_keywords"
    __table_args__ = {"schema": "staging"}

    staging_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("staging.research_objects.staging_id", ondelete="CASCADE"),
        primary_key=True,
    )
    keyword_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("reference.keywords.keyword_id"),
        primary_key=True,
    )

    # ── relationships ──────────────────────────────
    research_object: Mapped["StgResearchObject"] = relationship(  # noqa: F821
        "StgResearchObject",
        back_populates="keywords",
    )
    keyword: Mapped["Keyword"] = relationship("Keyword")  # noqa: F821