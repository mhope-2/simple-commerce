from typing import AsyncGenerator

from databases import Database
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.config.settings import settings

DATABASE_URL = f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}/{settings.DB_NAME}"

engine = create_async_engine(DATABASE_URL, echo=settings.DB_ECHO)

# Keep ORM objects usable after a request transaction commits. This is especially
# important for async FastAPI response serialization, which cannot perform an
# implicit database query to reload expired attributes.
session_maker = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()

database = Database(DATABASE_URL)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with session_maker() as session:
        yield session
