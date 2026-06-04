from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CreateOrder(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: str
    product_code: str
    quantity: int


class RetrieveOrder(CreateOrder):
    id: str
    customer_full_name: str
    product_name: str
    total_amount: float
    created_at: datetime
    updated_at: datetime


class OrderPayload(BaseModel):
    order_id: str
    customer_full_name: str
    product_name: str
    total_amount: float
    created_at: str


class OrderMessagePayload(BaseModel):
    order: OrderPayload


class OrderMessage(BaseModel):
    producer: str
    sent_at: str
    type: str
    payload: OrderMessagePayload
