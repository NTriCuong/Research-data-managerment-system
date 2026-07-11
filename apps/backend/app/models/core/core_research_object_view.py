import uuid
from datetime import date, datetime

from sqlalchemy import TIMESTAMP, Computed, Date, ForeignKey, Integer, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class CoreResearchObjectView(Base):
    __tablename__ = "research_object_views"
    __table_args__ = {"schema": "core"}

    view_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    research_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.research_objects.research_id", ondelete="CASCADE"),
        nullable=False,
    )
    viewed_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    viewed_date: Mapped[date] = mapped_column(
        Date,
        Computed(
            "(viewed_at AT TIME ZONE 'Asia/Ho_Chi_Minh')::DATE",
            persisted=True,
        ),
        nullable=False,
    )
    viewed_year: Mapped[int] = mapped_column(
        Integer,
        Computed(
            "EXTRACT(YEAR FROM viewed_at AT TIME ZONE 'Asia/Ho_Chi_Minh')::INT",
            persisted=True,
        ),
        nullable=False,
    )
    viewed_month: Mapped[int] = mapped_column(
        Integer,
        Computed(
            "EXTRACT(MONTH FROM viewed_at AT TIME ZONE 'Asia/Ho_Chi_Minh')::INT",
            persisted=True,
        ),
        nullable=False,
    )

    research_object: Mapped["CoreResearchObject"] = relationship(
        "CoreResearchObject", back_populates="views"
    )