from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repository import user_repository
from app.schemas.user import UserCreate, UserUpdate
from app.models.user import User
from app.core.security import get_password_hash
from app.core.exceptions import BadRequestException

class UserService:
    async def create_user(self, db: AsyncSession, user_in: UserCreate) -> User:
        user = await user_repository.get_by_email(db, email=user_in.email)
        if user:
            raise BadRequestException("User with this email already exists.")
        
        user_by_name = await user_repository.get_by_username(db, username=user_in.username)
        if user_by_name:
            raise BadRequestException("User with this username already exists.")

        create_data = user_in.model_dump()
        hashed_password = get_password_hash(create_data.pop("password"))
        create_data["hashed_password"] = hashed_password
        
        db_user = await user_repository.create(db, obj_in=create_data)
        return db_user

    async def get_user_by_id(self, db: AsyncSession, user_id: int) -> User | None:
        return await user_repository.get(db, id=user_id)

    async def search(self, db: AsyncSession, keyword: str, skip: int = 0, limit: int = 10):
        return await user_repository.search_users(db, keyword=keyword, skip=skip, limit=limit)

    async def update_user(self, db: AsyncSession, user_id: int, user_in: UserUpdate) -> User:
        db_user = await user_repository.get(db, id=user_id)
        if not db_user:
            raise BadRequestException("User not found.")
        
        update_data = user_in.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
            
        return await user_repository.update(db, db_obj=db_user, obj_in=update_data)

    async def delete_user(self, db: AsyncSession, user_id: int) -> User:
        db_user = await user_repository.get(db, id=user_id)
        if not db_user:
            raise BadRequestException("User not found.")
        # Soft delete
        return await user_repository.update(db, db_obj=db_user, obj_in={"is_deleted": True})

user_service = UserService()
