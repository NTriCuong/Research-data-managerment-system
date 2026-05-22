import uuid
from datetime import datetime

from sqlalchemy import TIMESTAMP, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.config import Base


class Keyword(Base):
    __tablename__ = "keywords"
    __table_args__ = {"schema": "reference"}

    keyword_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    keyword_text: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    normalized_text: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default="now()")