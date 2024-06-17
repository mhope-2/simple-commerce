from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_session
from app.schemas.order import CreateOrder
from app.services.order import fetch_order_record, create_order_record

order_router = APIRouter()


@order_router.get("/orders/{id}/")
async def retrieve_order(id: str, session: AsyncSession = Depends(get_session)):
    return await fetch_order_record(id, session)


@order_router.post("/orders/")
async def create_order(data: CreateOrder, background_tasks: BackgroundTasks, session: AsyncSession = Depends(get_session)):
    return await create_order_record(data, background_tasks, session)
