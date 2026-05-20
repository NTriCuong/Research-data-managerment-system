from datetime import datetime
from typing import Optional

from sqlalchemy import TEXT, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.config import Base


class Comment(Base):
    __tablename__ = "comments"

    # PK   | id          | INTEGER
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # FK,N | send_id     | VARCHAR(36) → users.id
    send_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )

    # FK,N | receiver_id | VARCHAR(36) → users.id
    receiver_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )

    # N    | context     | TEXT
    context: Mapped[str] = mapped_column(TEXT, nullable=False)

    # N    | create_at   | TIMESTAMP
    create_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=datetime.utcnow
    )

    # FK,N | research_id | INTEGER
    research_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("research.id"), nullable=True
    )

    sender   = relationship("User", foreign_keys=[send_id],     back_populates="sent_comments")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="recv_comments")