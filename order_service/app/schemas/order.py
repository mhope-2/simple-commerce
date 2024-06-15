from datetime import datetime

from pydantic import BaseModel


class CreateOrder(BaseModel):
    user_id: str
    product_code: str

    class Config:
        orm_mode = True


class RetrieveOrder(CreateOrder):
    id: int
    created_at: datetime
    updated_at: datetime

