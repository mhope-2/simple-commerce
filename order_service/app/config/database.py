
from databases import Database
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.config.settings import settings

DATABASE_URL = f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}/{settings.DB_NAME}"

# Create asynchronous engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create a configured "Session" class
session_maker = async_sessionmaker(engine)

# Base class for models
Base = declarative_base()

# Asynchronous database connection
database = Database(DATABASE_URL)


# Dependency to get the database session
async def get_session() -> AsyncSession:
    async with session_maker() as session:
        yield session
