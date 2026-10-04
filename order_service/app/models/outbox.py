import uuid

from sqlalchemy import JSON, TIMESTAMP, Column, Index, String, func

from app.config.database import Base


class OutboxEvent(Base):
    __tablename__ = "outbox_events"
    __table_args__ = (Index("ix_outbox_events_status_created_at", "status", "created_at"),)

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    event_type = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)
    status = Column(String, nullable=False, default="pending", server_default="pending")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    published_at = Column(TIMESTAMP(timezone=True), nullable=True)
