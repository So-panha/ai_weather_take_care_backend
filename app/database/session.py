from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
    pool_size=5,
    max_overflow=10
)

async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)

async def get_db():
    """ Dependency for getting async session """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
