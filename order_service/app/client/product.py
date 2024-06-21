from app.config.settings import settings
from dataclasses import dataclass
from typing import Optional

import httpx
from fastapi import HTTPException, status
from tenacity import retry, stop_after_attempt, stop_after_delay, wait_fixed


@dataclass
class Product:
    """Class to represent a Product object"""

    code: str
    name: str
    price: float


class ProductService:
    """
    Utility class to define requests to the Product Service
    """

    @staticmethod
    @retry(
        stop=(stop_after_attempt(3) | stop_after_delay(5)),  # stop after 3 attempts or 5 seconds
        wait=wait_fixed(2)  # wait 2 seconds between retries
    )
    async def fetch_product(code: str) -> Optional[Product]:
        product_service_url = settings.PRODUCT_SERVICE_URL

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{product_service_url}/{code}/") # returns a 307 without trailing backslash
                if response.status_code == status.HTTP_200_OK:
                    data = response.json()
                    return Product(**data)

                elif response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Product service returned a server error",
                    )

                elif response.status_code == status.HTTP_404_NOT_FOUND:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Product service returned 404",
                    )

                else:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Received non-200 status code from Product Service: {response.status_code}",
                    )

            except httpx.HTTPError:
                raise HTTPException(
                    status_code=status.HTTP_408_REQUEST_TIMEOUT,
                    detail="Request to product service timed out"
                )

            except httpx.RequestError as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Request to product service failed: {str(e)}"
                )
