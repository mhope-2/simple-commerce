import asyncio
import logging

from app.config.database import session_maker
from app.services.outbox import publish_one_pending_event

logger = logging.getLogger(__name__)


async def run() -> None:
    while True:
        try:
            async with session_maker() as session:
                published = await publish_one_pending_event(session)
        except Exception:
            logger.exception("Outbox worker database operation failed; retrying")
            published = False

        if not published:
            await asyncio.sleep(1)


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        logger.info("Outbox worker stopped")
