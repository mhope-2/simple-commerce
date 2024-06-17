import logging
import os

import pika

logger = logging.getLogger(__name__)


class Producer(object):
    def __init__(self, host, exchange, exchange_type, routing_key):
        self.host = host
        self.exchange = exchange
        self.exchange_type = exchange_type
        self.routing_key = routing_key or ""

    def connection(self):
        credentials = pika.PlainCredentials(os.getenv("RABBITMQ_DEFAULT_USER"), os.getenv("RABBITMQ_DEFAULT_PASS"))
        return pika.BlockingConnection(
            pika.ConnectionParameters(host=self.host, credentials=credentials)
        )

    def channel(self):
        return self.connection().channel()

    def exchange_declare(self):
        return self.channel().exchange_declare(exchange=self.exchange, exchange_type=self.exchange_type)

    def close_connection(self):
        self.connection().close()

    def publish(self, message):
        log_msg = f"Published message to {self.exchange}; msg={message}"

        self.exchange_declare()

        self.channel().basic_publish(exchange=self.exchange, routing_key=self.routing_key, body=message)

        logger.info(log_msg)
        print(log_msg)

        self.close_connection()
