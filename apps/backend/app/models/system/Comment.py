from datetime import datetime
from typing import Optional

from sqlalchemy import TEXT, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.config import Base


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    send_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )

    receiver_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )

    context: Mapped[str] = mapped_column(TEXT, nullable=False)

    create_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=datetime.utcnow
    )

    research_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("research.id"), nullable=True
    )

    sender   = relationship("User", foreign_keys=[send_id],     back_populates="sent_comments")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="recv_comments")