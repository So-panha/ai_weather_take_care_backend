from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.repositories.base_repository import BaseRepository
from app.models.user import User

class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(User)

    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        query = select(User).filter(User.email == email, User.is_deleted == False)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_username(self, db: AsyncSession, username: str) -> User | None:
        query = select(User).filter(User.username == username, User.is_deleted == False)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def search_users(self, db: AsyncSession, keyword: str, skip: int = 0, limit: int = 10) -> tuple[list[User], int]:
        base_query = select(User).filter(User.is_deleted == False)
        if keyword:
            base_query = base_query.filter(
                (User.username.ilike(f"%{keyword}%")) | (User.email.ilike(f"%{keyword}%"))
            )
        
        count_query = select(func.count()).select_from(base_query.subquery())
        total = await db.scalar(count_query)

        data_query = base_query.offset(skip).limit(limit)
        result = await db.execute(data_query)
        users = list(result.scalars().all())
        
        return users, total

user_repository = UserRepository()
