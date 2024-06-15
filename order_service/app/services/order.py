from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.client.product import ProductService
from app.client.user import UserService
from app.models.order import Order
from app.schemas.order import CreateOrder


async def fetch_order_record(id: str, session: AsyncSession):
    async with session.begin():
        result = await session.execute(select(Order).where(Order.id == id))
        order = result.scalars().first()

    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


async def create_order_record(data: CreateOrder, session: AsyncSession):
    async with session.begin():
        try:
            user = await UserService.fetch_user(data.user_id)
            product = await ProductService.fetch_product(data.product_code)

            if user and product:
                order = Order(user_id=user.id, product_id=product.id)
                session.add(order)

                try:
                    await session.commit()
                    await session.refresh(order)
                except Exception as e:
                    await session.rollback()
                    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

        except HTTPException as e:
            raise e
