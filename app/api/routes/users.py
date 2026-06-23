import os
import uuid
from pathlib import Path
from fastapi import APIRouter, Query, UploadFile, File, HTTPException
from typing import List
from app.api.deps import SessionDep, CurrentUser, CurrentAdmin
from app.schemas.user import UserResponse, UserUpdate
from app.services.user_service import user_service
from app.core.exceptions import NotFoundException

UPLOAD_DIR = Path("uploads/avatars")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: CurrentUser):
    """
    Get current user profile.
    """
    return current_user

@router.post("/me/avatar", response_model=UserResponse)
async def upload_avatar(
    db: SessionDep,
    current_user: CurrentUser,
    file: UploadFile = File(...)
):
    """
    Upload a profile avatar image.
    """
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="File must be an image (JPEG, PNG, WebP, or GIF)")
    
    # Max 5MB
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Maximum 5MB.")
    
    ext = file.filename.rsplit(".", 1)[-1] if "." in file.filename else "jpg"
    filename = f"{current_user.id}_{uuid.uuid4().hex[:8]}.{ext}"
    filepath = UPLOAD_DIR / filename
    
    with open(filepath, "wb") as f:
        f.write(contents)
    
    avatar_url = f"/uploads/avatars/{filename}"
    user_update = UserUpdate(avatar_url=avatar_url)
    return await user_service.update_user(db, user_id=current_user.id, user_in=user_update)

@router.put("/me", response_model=UserResponse)
async def update_user_me(db: SessionDep, current_user: CurrentUser, user_in: UserUpdate):
    """
    Update current user profile.
    """
    return await user_service.update_user(db, user_id=current_user.id, user_in=user_in)

@router.get("/", response_model=List[UserResponse])
async def read_users(db: SessionDep, current_user: CurrentAdmin, skip: int = 0, limit: int = 100):
    """
    Retrieve users (Admin only).
    """
    users, _ = await user_service.search(db, keyword="", skip=skip, limit=limit)
    return users

@router.get("/search", response_model=dict)
async def search_users(
    db: SessionDep, 
    current_user: CurrentAdmin, 
    keyword: str = Query(""), 
    skip: int = 0, 
    limit: int = 10
):
    """
    Search users with pagination (Admin only).
    """
    users, total = await user_service.search(db, keyword=keyword, skip=skip, limit=limit)
    return {
        "total": total, 
        "users": [UserResponse.model_validate(u).model_dump() for u in users]
    }

@router.get("/{user_id}", response_model=UserResponse)
async def read_user_by_id(user_id: int, db: SessionDep, current_user: CurrentAdmin):
    """
    Get a specific user by id (Admin only).
    """
    user = await user_service.get_user_by_id(db, user_id=user_id)
    if not user:
        raise NotFoundException("User not found")
    return user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_in: UserUpdate, db: SessionDep, current_user: CurrentAdmin):
    """
    Update a user (Admin only).
    """
    return await user_service.update_user(db, user_id=user_id, user_in=user_in)

@router.delete("/{user_id}", response_model=UserResponse)
async def delete_user(user_id: int, db: SessionDep, current_user: CurrentAdmin):
    """
    Soft delete a user (Admin only).
    """
    return await user_service.delete_user(db, user_id=user_id)
