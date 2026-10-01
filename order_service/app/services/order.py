import logging
from datetime import datetime, timezone
from fastapi import BackgroundTasks, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from tenacity import retry, stop_after_attempt, stop_after_delay, wait_fixed

from app.client.product import ProductService
from app.client.user import UserService
from app.config.metrics import MESSAGES_PUBLISHED, ORDERS_CREATED, ORDERS_FAILED, count_retry
from app.config.settings import settings
from app.messaging.rabbitmq.producer import Producer
from app.models.order import Order
from app.schemas.order import CreateOrder, OrderMessage, OrderMessagePayload, OrderPayload

logger = logging.getLogger(__name__)


async def fetch_order_record(id: str, session: AsyncSession) -> Order:
    async with session.begin():
        result = await session.execute(select(Order).where(Order.id == id))
        order = result.scalars().first()

    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@retry(
    stop=(stop_after_attempt(3) | stop_after_delay(5)),  # stop after 3 attempts or 5 seconds
    wait=wait_fixed(2),  # wait 2 seconds between retries
    before_sleep=count_retry("rabbitmq"),
)
def _publish(json_message: str) -> None:
    producer = Producer(
        settings.RABBITMQ_HOST,
        settings.EXCHANGE,
        settings.EXCHANGE_TYPE,
        settings.ROUTING_KEY,
    )
    producer.publish(json_message)


def publish_message(message: OrderMessage) -> None:
    try:
        _publish(message.model_dump_json())
    except Exception:
        MESSAGES_PUBLISHED.add(1, {"outcome": "failure"})
        raise
    MESSAGES_PUBLISHED.add(1, {"outcome": "success"})


async def create_order_record(
    data: CreateOrder, background_tasks: BackgroundTasks, session: AsyncSession
) -> Order | None:
    try:
        user = await UserService.fetch_user(data.user_id)
        product = await ProductService.fetch_product(data.product_code)

        if not user or not product:
            ORDERS_FAILED.add(1, {"error.type": "missing_user_or_product"})
            return None

        total_price = product.price * data.quantity  # type: ignore[union-attr]

        order = Order(
            user_id=user.id,  # type: ignore[union-attr]
            product_code=product.code,  # type: ignore[union-attr]
            product_name=product.name,  # type: ignore[union-attr]
            customer_full_name=f"{user.first_name} {user.last_name}",  # type: ignore[union-attr]
            quantity=data.quantity,
            total_amount=total_price,
        )
        session.add(order)
        await session.commit()
        await session.refresh(order)

        order_payload = OrderPayload(
            order_id=order.id,
            customer_full_name=order.customer_full_name,
            product_name=order.product_name,
            total_amount=order.total_amount,
            created_at=order.created_at.isoformat(),
        )

        message = OrderMessage(
            producer="order_service",
            sent_at=datetime.now(timezone.utc).isoformat(),
            type="created_order",
            payload=OrderMessagePayload(order=order_payload),
        )

        background_tasks.add_task(publish_message, message=message)

        ORDERS_CREATED.add(1, {"product.code": data.product_code})
        return order

    except HTTPException as e:
        ORDERS_FAILED.add(1, {"error.type": str(e.status_code)})
        logger.error(str(e))
        raise e

    except SQLAlchemyError as e:
        ORDERS_FAILED.add(1, {"error.type": "database"})
        logger.error("Failed to save order", exc_info=True)
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error saving order")

    except Exception as e:
        ORDERS_FAILED.add(1, {"error.type": type(e).__name__})
        logger.exception("Unexpected error in create_order_record")
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Exception occurred")
