from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.order import Order


async def fetch_order(id: str, session: AsyncSession):
    async with session.begin():
        result = await session.execute(select(Order).where(Order.id == id))
        order = result.scalars().first()

    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


# def get_order