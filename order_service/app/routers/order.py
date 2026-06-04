from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_session
from app.models.order import Order
from app.schemas.order import CreateOrder, RetrieveOrder
from app.services.order import create_order_record, fetch_order_record

order_router = APIRouter(prefix="/orders")


@order_router.get("/{id}/", response_model=RetrieveOrder)
async def retrieve_order(id: str, session: AsyncSession = Depends(get_session)) -> Order:
    return await fetch_order_record(id, session)


@order_router.post("/")
async def create_order(
    data: CreateOrder, background_tasks: BackgroundTasks, session: AsyncSession = Depends(get_session)
) -> Order | None:
    return await create_order_record(data, background_tasks, session)
