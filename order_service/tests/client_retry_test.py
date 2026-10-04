from unittest.mock import AsyncMock, patch

import httpx
import pytest
from fastapi import HTTPException
from tenacity import wait_none

from app.client.product import ProductService
from app.client.user import UserService


@pytest.fixture(autouse=True)
def no_retry_wait():
    # Retry immediately in tests instead of waiting for the production backoff.
    with patch.object(UserService.fetch_user.retry, "wait", wait_none()), \
            patch.object(ProductService.fetch_product.retry, "wait", wait_none()):
        yield


def response(status_code: int) -> httpx.Response:
    return httpx.Response(status_code, json={}, request=httpx.Request("GET", "http://test"))


@pytest.mark.asyncio
async def test_not_found_is_not_retried():
    get = AsyncMock(return_value=response(404))
    with patch("httpx.AsyncClient.get", get), pytest.raises(HTTPException) as exc:
        await UserService.fetch_user("unknown")
    assert exc.value.status_code == 404
    assert get.await_count == 1


@pytest.mark.asyncio
async def test_server_error_is_retried_then_reraised():
    get = AsyncMock(return_value=response(500))
    with patch("httpx.AsyncClient.get", get), pytest.raises(HTTPException) as exc:
        await ProductService.fetch_product("product3")
    assert exc.value.status_code == 500
    assert get.await_count == 3


@pytest.mark.asyncio
async def test_retry_succeeds_after_server_error():
    get = AsyncMock(side_effect=[
        response(500),
        httpx.Response(200, json={"code": "product1", "name": "Product 1", "price": 9.99},
                       request=httpx.Request("GET", "http://test")),
    ])
    with patch("httpx.AsyncClient.get", get):
        product = await ProductService.fetch_product("product1")
    assert product is not None and product.code == "product1"
    assert get.await_count == 2
