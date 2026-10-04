import pytest
import pytest_asyncio
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from unittest.mock import patch, AsyncMock

from app.main import app
from app.client.user import User
from app.client.product import Product
from app.config.database import get_session


DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/orders"

# TestClient runs the app on its own event loop, so connections must not be pooled
# across loops, and each request gets its own session (as get_session does).
engine = create_async_engine(DATABASE_URL, poolclass=NullPool)

async_session = async_sessionmaker(engine, expire_on_commit=False)


@pytest_asyncio.fixture()
async def test_session():
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture()
async def test_client():
    async def override_get_session():
        async with async_session() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def mock_fetch_user():
    with patch(
            "app.client.user.UserService.fetch_user",
            AsyncMock(return_value=User(id="7c11e1ce2741", first_name="John", last_name="Doe"))
    ) as mocked:
        yield mocked


@pytest.fixture
def mock_fetch_product():
    async def fetch_product(code):
        if code == "product3":
            raise RuntimeError("Product service failed")
        return Product(code="product1", name="Product 1", price=9.99)

    with patch(
        "app.client.product.ProductService.fetch_product",
        AsyncMock(side_effect=fetch_product),
    ) as mocked:
        yield mocked

@pytest.fixture
def mock_fetch_user_not_found():
    with patch(
        "app.client.user.UserService.fetch_user",
        AsyncMock(side_effect=HTTPException(status_code=404, detail="User service returned a 404")),
    ) as mocked:
        yield mocked


@pytest.fixture
def mock_fetch_product_not_found():
    with patch(
        "app.client.product.ProductService.fetch_product",
        AsyncMock(side_effect=HTTPException(status_code=404, detail="Product service returned 404")),
    ) as mocked:
        yield mocked


@pytest.fixture
def mock_fetch_product_error():
    with patch(
        "app.client.product.ProductService.fetch_product",
        AsyncMock(side_effect=RuntimeError("unexpected")),
    ) as mocked:
        yield mocked
