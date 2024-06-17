import uuid

from sqlalchemy import TIMESTAMP, Column, Float, Integer, String, func

from app.config.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    product_code = Column(String, nullable=True, index=True)
    customer_full_name = Column(String, nullable=False)
    product_name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    total_amount = Column(Float, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
