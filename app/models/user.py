from sqlalchemy import String, Boolean, Integer, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
import enum
from app.database.base import Base

class Role(str, enum.Enum):
    ADMIN = "ADMIN"
    USER = "USER"

class UserStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    LOCKED = "LOCKED"

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str | None] = mapped_column(String, nullable=True)
    full_name: Mapped[str | None] = mapped_column(String, nullable=True)
    location: Mapped[str | None] = mapped_column(String, nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String, nullable=True)

    role: Mapped[Role] = mapped_column(SQLEnum(Role), default=Role.USER, nullable=False)
    status: Mapped[UserStatus] = mapped_column(SQLEnum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
