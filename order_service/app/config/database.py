from typing import AsyncGenerator

from databases import Database
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.config.settings import settings

DATABASE_URL = f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}/{settings.DB_NAME}"

engine = create_async_engine(DATABASE_URL, echo=settings.DB_ECHO)

# Keep loaded attributes after commit: responses are serialized after the session's
# transaction has ended, when lazy loading is no longer possible.
session_maker = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()

database = Database(DATABASE_URL)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with session_maker() as session:
        yield session
