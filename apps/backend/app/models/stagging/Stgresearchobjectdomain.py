"""
Model: StgResearchObjectDomain
Schema: staging
Table:  staging.research_object_domains

SQL gốc:
    CREATE TABLE IF NOT EXISTS staging.research_object_domains (
        staging_id  UUID NOT NULL REFERENCES staging.research_objects ON DELETE CASCADE,
        domain_id   UUID NOT NULL REFERENCES reference.research_domains,
        PRIMARY KEY (staging_id, domain_id)
    );
"""

import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.config import Base


class StgResearchObjectDomain(Base):
    __tablename__ = "research_object_domains"
    __table_args__ = {"schema": "staging"}

    staging_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("staging.research_objects.staging_id", ondelete="CASCADE"),
        primary_key=True,
    )
    domain_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("reference.research_domains.domain_id"),
        primary_key=True,
    )

    # ── relationships ──────────────────────────────
    research_object: Mapped["StgResearchObject"] = relationship(  # noqa: F821
        "StgResearchObject",
        back_populates="domains",
    )
    domain: Mapped["ResearchDomain"] = relationship("ResearchDomain")  # noqa: F821