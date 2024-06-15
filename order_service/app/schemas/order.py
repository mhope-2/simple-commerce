from datetime import datetime

from pydantic import BaseModel


class CreateOrder(BaseModel):
    user_id: str
    product_code: str
    quantity: int

    class Config:
        from_attributes = True


class RetrieveOrder(CreateOrder):
    id: int
    customer_full_name: str
    product_name: str
    total_amount: float
    created_at: datetime
    updated_at: datetime
