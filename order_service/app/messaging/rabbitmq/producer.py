import logging

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

    def publish(self, message: str, message_id: str | None = None, event_type: str | None = None) -> None:
        log_msg = f"Published message to {self.exchange}; msg={message}"

        connection = self.connection()
        try:
            channel = connection.channel()
            channel.exchange_declare(exchange=self.exchange, exchange_type=self.exchange_type, durable=True)
            channel.confirm_delivery()
            channel.basic_publish(
                exchange=self.exchange,
                routing_key=self.routing_key,
                body=message,
                mandatory=True,
                properties=pika.BasicProperties(
                    content_type="application/json",
                    delivery_mode=2,
                    message_id=message_id,
                    type=event_type,
                ),
            )
            logger.info(log_msg)
        finally:
            connection.close()
