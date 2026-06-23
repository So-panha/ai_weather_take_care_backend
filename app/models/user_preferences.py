from sqlalchemy import Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

class UserPreference(Base):
    __tablename__ = "user_preferences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), unique=True, index=True, nullable=False)
    
    # Appearance
    dark_mode: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    compact_view: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    reduce_animations: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Notifications
    push_alerts: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    storm_warning: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # System
    location_services: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
