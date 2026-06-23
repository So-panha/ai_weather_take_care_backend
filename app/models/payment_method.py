from sqlalchemy import String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base

class PaymentMethod(Base):
    __tablename__ = "payment_methods"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    
    card_type: Mapped[str] = mapped_column(String, nullable=False) # e.g., 'Visa', 'Mastercard'
    last4: Mapped[str] = mapped_column(String(4), nullable=False)
    expiry: Mapped[str] = mapped_column(String(5), nullable=False) # e.g., '12/26'
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    bg_gradient: Mapped[str | None] = mapped_column(String, nullable=True)
