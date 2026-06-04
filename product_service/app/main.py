import time

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI(title="Product Service")


class ProductResponse(BaseModel):
    code: str
    name: str
    price: float


@app.get("/products/{code}/", response_model=ProductResponse)
async def retrieve(code: str) -> ProductResponse:
    """
    Returns a product by code
    :return:
    """

    if not code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please provide a product code")

    if code == "product1":
        time.sleep(0.2)

        return ProductResponse(code="product1", name="Product 1", price=9.99)

    elif code == "product2":
        time.sleep(60)

        return ProductResponse(code="product2", name="Product 2", price=14.99)

    elif code == "product3":
        time.sleep(0.2)
        raise HTTPException(status_code=500, detail="Internal Server Error")

    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")