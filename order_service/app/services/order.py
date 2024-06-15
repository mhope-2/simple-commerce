from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
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
    try:
        user = await UserService.fetch_user(data.user_id)
        product = await ProductService.fetch_product(data.product_code)

        if user and product:
            total_price = product.price * data.quantity

            order = Order(
                user_id=user.id,
                product_code=product.code,
                product_name=product.name,
                customer_full_name=f"{user.first_name} {user.last_name}",
                quantity=data.quantity,
                total_amount=total_price,
            )
            session.add(order)
            await session.commit()
            await session.refresh(order)

            # TODO: CALL BG func to push order to RabbitMQ

            return order

    except HTTPException as e:
        print(str(e))
        raise e

    except SQLAlchemyError as e:
        print(str(e))
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error saving order")

    except Exception as e:
        print(str(e))
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error saving order")

