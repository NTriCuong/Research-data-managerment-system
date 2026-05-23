import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.config import Base
from app.models.reference.research_domain import ResearchDomain  # noqa: F401
from app.models.stagging.stg_research_object import StgResearchObject  # noqa: F401


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