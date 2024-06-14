import time

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse

app = FastAPI(title="Product Service")


@app.get("/products/{code}/")
async def retrieve(code: str):
    """
    Returns a product by code
    :return:
    """

    if not code:
        return JSONResponse(status_code=400, content={"message": "Please provide a product code"})

    if code == "product1":
        time.sleep(0.2)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"code": "product1", "name": "Product 1", "price": 9.99}
        )

    elif code == "product2":
        time.sleep(60)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"code": "product2", "name": "Product 2", "price": 14.99}
    )

    elif code == "product3":
        time.sleep(0.2)
        raise HTTPException(status_code=500, detail="Internal Server Error")

    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")