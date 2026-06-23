from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from app.models.user import Role, UserStatus

class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    password: Optional[str] = Field(None, min_length=8)
    full_name: Optional[str] = None
    location: Optional[str] = None
    avatar_url: Optional[str] = None

class UserResponse(UserBase):
    id: int
    role: Role
    status: UserStatus
    is_deleted: bool
    full_name: Optional[str] = None
    location: Optional[str] = None
    avatar_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
