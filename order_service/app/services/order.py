import logging
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.client.product import ProductService
from app.client.user import UserService
from app.config.metrics import ORDERS_CREATED, ORDERS_FAILED
from app.models.order import Order
from app.models.outbox import OutboxEvent
from app.schemas.order import CreateOrder, OrderMessage, OrderMessagePayload, OrderPayload

logger = logging.getLogger(__name__)


async def fetch_order_record(order_id: str, session: AsyncSession) -> Order:
    async with session.begin():
        result = await session.execute(select(Order).where(Order.id == order_id))
        order = result.scalars().first()

    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


async def create_order_record(
    data: CreateOrder, session: AsyncSession
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
        async with session.begin():
            session.add(order)
            await session.flush()
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

            session.add(
                OutboxEvent(
                    event_type=message.type,
                    payload=message.model_dump(mode="json"),
                )
            )

        ORDERS_CREATED.add(1, {"product.code": data.product_code})
        return order

    except HTTPException as e:
        ORDERS_FAILED.add(1, {"error.type": str(e.status_code)})
        logger.error(str(e))
        raise e

    except SQLAlchemyError:
        ORDERS_FAILED.add(1, {"error.type": "database"})
        logger.error("Failed to save order", exc_info=True)
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error saving order")

    except Exception as e:
        ORDERS_FAILED.add(1, {"error.type": type(e).__name__})
        logger.exception("Unexpected error in create_order_record")
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Exception occurred")
