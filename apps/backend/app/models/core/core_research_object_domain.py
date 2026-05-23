"""
Model: CoreResearchObjectDomain
Schema: core
Table:  core.research_object_domains

SQL gốc:
    CREATE TABLE IF NOT EXISTS core.research_object_domains (
        research_id UUID NOT NULL REFERENCES core.research_objects ON DELETE CASCADE,
        domain_id   UUID NOT NULL REFERENCES reference.research_domains,
        PRIMARY KEY (research_id, domain_id)
    );
"""

import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.config import Base
from app.models.reference.research_domain import ResearchDomain  # noqa: F401
from app.models.core.core_research_object import CoreResearchObject  # noqa: F401


class CoreResearchObjectDomain(Base):
    __tablename__ = "research_object_domains"
    __table_args__ = {"schema": "core"}

    research_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.research_objects.research_id", ondelete="CASCADE"),
        primary_key=True,
    )
    domain_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("reference.research_domains.domain_id"),
        primary_key=True,
    )

    # ── relationships ──────────────────────────────
    research_object: Mapped["CoreResearchObject"] = relationship(  # noqa: F821
        "CoreResearchObject",
        back_populates="domains",
    )
    domain: Mapped["ResearchDomain"] = relationship("ResearchDomain")  # noqa: F821