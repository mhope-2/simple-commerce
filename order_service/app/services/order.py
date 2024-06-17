import json
import logging
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from tenacity import retry, stop_after_attempt, stop_after_delay, wait_fixed

from app.client.product import ProductService
from app.client.user import UserService
from app.config.settings import settings
from app.messaging.rabbitmq.producer import Producer
from app.models.order import Order
from app.schemas.order import CreateOrder

logger = logging.getLogger(__name__)


async def fetch_order_record(id: str, session: AsyncSession):
    async with session.begin():
        result = await session.execute(select(Order).where(Order.id == id))
        order = result.scalars().first()

    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@retry(
    stop=(stop_after_attempt(3) | stop_after_delay(5)),  # stop after 3 attempts or 5 seconds
    wait=wait_fixed(2)  # wait 2 seconds between retries
)
def publish_message(message):
    json_message = json.dumps(message)

    producer = Producer(
        settings.RABBITMQ_HOST,
        settings.EXCHANGE,
        settings.EXCHANGE_TYPE,
        settings.ROUTING_KEY,
    )
    producer.publish(json_message)


async def create_order_record(data: CreateOrder, background_tasks, session: AsyncSession):
    try:
        user = await UserService.fetch_user(data.user_id)
        product = await ProductService.fetch_product(data.product_code)

        if not user and product:
            return

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

        order_payload = dict(
            order_id=order.id,
            customer_full_name=order.customer_full_name,
            product_name=order.product_name,
            total_amount=order.total_amount,
            created_at=order.created_at.isoformat(), # convert to ISO format for JSON serialization
        )

        message = {
            "producer": "order_service",
            "sent_at": datetime.now(timezone.utc).isoformat(), # convert to ISO format for JSON serialization
            "type": "created_order",
            "payload": {
                "order": order_payload,
            },
        }

        # invoke background task to publish message
        #https://fastapi.tiangolo.com/tutorial/background-tasks/
        background_tasks.add_task(publish_message, message=message)

        return order

    except HTTPException as e:
        print("Error: ", e)
        logger.error(str(e))
        raise e

    except SQLAlchemyError as e:
        print("Error: ", e)
        logger.error(str(e))
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error saving order")

    except Exception as e:
        print("Error: ", e)
        logger.error(str(e))
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Exception occurred")

