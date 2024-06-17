import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from unittest.mock import patch, AsyncMock

from app.main import app
from app.client.user import User
from app.client.product import Product
from sqlalchemy.orm import declarative_base
from app.config.database import get_session
import pytest_asyncio


DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/orders"

Base = declarative_base()

engine = create_async_engine(DATABASE_URL, echo=True)

async_session = async_sessionmaker(engine)


@pytest_asyncio.fixture()
@pytest.mark.asyncio
async def test_session():
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture()
@pytest.mark.asyncio
async def test_client(test_session):
    async def override_get_session():
        try:
            yield test_session
        finally:
            await test_session.close()

    app.dependency_overrides[get_session] = override_get_session
    yield TestClient(app)


@pytest.fixture
def mock_fetch_user():
    with patch(
            "app.client.user.UserService.fetch_user",
            AsyncMock(return_value=User(id="7c11e1ce2741", first_name="John", last_name="Doe"))
    ) as mocked:
        yield mocked


@pytest.fixture
def mock_fetch_product():
    with patch(
            "app.client.product.ProductService.fetch_product",
            AsyncMock(return_value=Product(code="product1", name="Product 1", price=9.99))
    ) as mocked:
        yield mocked

@pytest.fixture
def mock_publish_message():
    with patch("app.services.order.publish_message", AsyncMock(return_value=None)) as mocked:
        yield mocked
