import asyncio
import json
import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from tenacity import retry, stop_after_attempt, stop_after_delay, wait_fixed

from app.config.metrics import MESSAGES_PUBLISHED, count_retry
from app.config.settings import settings
from app.messaging.rabbitmq.producer import Producer
from app.models.outbox import OutboxEvent

logger = logging.getLogger(__name__)


@retry(
    stop=(stop_after_attempt(3) | stop_after_delay(5)),
    wait=wait_fixed(2),
    before_sleep=count_retry("rabbitmq"),
    reraise=True,
)
def _publish_event(event: OutboxEvent) -> None:
    Producer(
        settings.RABBITMQ_HOST,
        settings.EXCHANGE,
        settings.EXCHANGE_TYPE,
        settings.ROUTING_KEY,
    ).publish(
        event.payload if isinstance(event.payload, str) else _serialize_payload(event.payload),
        message_id=event.id,
        event_type=event.event_type,
    )


def publish_event(event: OutboxEvent) -> None:
    try:
        _publish_event(event)
    except Exception:
        MESSAGES_PUBLISHED.add(1, {"outcome": "failure"})
        raise
    MESSAGES_PUBLISHED.add(1, {"outcome": "success"})


def _serialize_payload(payload: object) -> str:
    return json.dumps(payload)


async def publish_one_pending_event(session: AsyncSession) -> bool:
    """Publish one event while holding its row lock.

    If publishing succeeds but the database commit fails, the event is published again.
    Consumers must therefore treat the outbox event/message ID as an idempotency key.
    """
    try:
        async with session.begin():
            result = await session.execute(
                select(OutboxEvent)
                .where(OutboxEvent.status == "pending")
                .order_by(OutboxEvent.created_at, OutboxEvent.id)
                .with_for_update(skip_locked=True)
                .limit(1)
            )
            event = result.scalars().first()
            if event is None:
                return False

            await asyncio.to_thread(publish_event, event)
            event.status = "published"
            event.published_at = datetime.now(timezone.utc)
            return True
    except Exception:
        logger.exception("Failed to publish an outbox event; it will be retried")
        return False
