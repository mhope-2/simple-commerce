import logging
from typing import Any

import pika

from app.config.settings import settings

logger = logging.getLogger(__name__)


class Producer:
    def __init__(self, host: str, exchange: str, exchange_type: str, routing_key: str) -> None:
        self.host = host
        self.exchange = exchange
        self.exchange_type = exchange_type
        self.routing_key = routing_key or ""

    def connection(self) -> pika.BlockingConnection:
        credentials = pika.PlainCredentials(settings.RABBITMQ_DEFAULT_USER, settings.RABBITMQ_DEFAULT_PASS)
        return pika.BlockingConnection(
            pika.ConnectionParameters(host=self.host, credentials=credentials)
        )

    def channel(self) -> Any:
        return self.connection().channel()

    def exchange_declare(self) -> Any:
        return self.channel().exchange_declare(exchange=self.exchange, exchange_type=self.exchange_type)

    def close_connection(self) -> None:
        self.connection().close()

    def publish(self, message: str) -> None:
        log_msg = f"Published message to {self.exchange}; msg={message}"

        self.exchange_declare()

        self.channel().basic_publish(exchange=self.exchange, routing_key=self.routing_key, body=message)

        logger.info(log_msg)

        self.close_connection()
