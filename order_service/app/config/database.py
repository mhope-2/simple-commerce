import os

from databases import Database
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

DATABASE_URL = f"postgresql+asyncpg://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"

# Create asynchronous engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create a configured "Session" class
async_session = async_sessionmaker(
    engine
)

# Base class for models
Base = declarative_base()

# Asynchronous database connection
database = Database(DATABASE_URL)


# Dependency to get the database session
async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
