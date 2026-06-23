from sqlalchemy import String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import JSONB

class ConsultationHistory(Base):
    __tablename__ = "consultation_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    
    title: Mapped[str] = mapped_column(String, nullable=False)
    text: Mapped[str] = mapped_column(String, nullable=False)
    tags: Mapped[list[str]] = mapped_column(JSONB, default=list, server_default='[]', nullable=False)
    icon: Mapped[str] = mapped_column(String, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
