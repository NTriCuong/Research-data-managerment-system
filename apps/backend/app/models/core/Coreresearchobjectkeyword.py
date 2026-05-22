"""
Model: CoreResearchObjectKeyword
Schema: core
Table:  core.research_object_keywords

SQL gốc:
    CREATE TABLE IF NOT EXISTS core.research_object_keywords (
        research_id UUID NOT NULL REFERENCES core.research_objects ON DELETE CASCADE,
        keyword_id  UUID NOT NULL REFERENCES reference.keywords,
        PRIMARY KEY (research_id, keyword_id)
    );
"""

import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.config import Base


class CoreResearchObjectKeyword(Base):
    __tablename__ = "research_object_keywords"
    __table_args__ = {"schema": "core"}

    research_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.research_objects.research_id", ondelete="CASCADE"),
        primary_key=True,
    )
    keyword_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("reference.keywords.keyword_id"),
        primary_key=True,
    )

    # ── relationships ──────────────────────────────
    research_object: Mapped["CoreResearchObject"] = relationship(  # noqa: F821
        "CoreResearchObject",
        back_populates="keywords",
    )
    keyword: Mapped["Keyword"] = relationship("Keyword")  # noqa: F821