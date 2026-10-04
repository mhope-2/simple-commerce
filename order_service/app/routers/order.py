from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_session
from app.models.order import Order
from app.schemas.order import CreateOrder, RetrieveOrder
from app.services.order import create_order_record, fetch_order_record

order_router = APIRouter(prefix="/orders")


@order_router.get("/{order_id}/", response_model=RetrieveOrder)
async def retrieve_order(order_id: str, session: AsyncSession = Depends(get_session)) -> Order:
    return await fetch_order_record(order_id, session)


@order_router.post("/", response_model=RetrieveOrder | None)
async def create_order(
    data: CreateOrder, session: AsyncSession = Depends(get_session)
) -> Order | None:
    return await create_order_record(data, session)
