from fastapi import APIRouter, Depends

from app.services.order import fetch_order

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.config.database import get_session

order_router = APIRouter()

@order_router.get("/orders/{id}")
# TODO: fix routing and service naming conventions
async def retrieve_order(id: str, session: AsyncSession = Depends(get_session)):
    return await fetch_order(id, session)
