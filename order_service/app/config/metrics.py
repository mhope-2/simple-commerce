"""Business metrics for the order service.

They use the global OpenTelemetry meter provider, which FastAPI sets up from the
environment at startup, and reach Prometheus through the collector as
orders_created_total, orders_failed_total, orders_messages_published_total and
orders_dependency_retries_total. Without an OTLP endpoint they are no-ops.
"""

from collections.abc import Callable

from opentelemetry import metrics
from tenacity import RetryCallState

_meter = metrics.get_meter("app.order_service")

ORDERS_CREATED = _meter.create_counter(
    "orders.created", unit="{order}", description="Orders saved to the database."
)
ORDERS_FAILED = _meter.create_counter(
    "orders.failed", unit="{order}", description="Order requests that did not create an order, by error.type."
)
MESSAGES_PUBLISHED = _meter.create_counter(
    "orders.messages.published",
    unit="{message}",
    description="Order messages sent to RabbitMQ, by outcome (success or failure, after retries).",
)
DEPENDENCY_RETRIES = _meter.create_counter(
    "orders.dependency.retries",
    unit="{retry}",
    description="Retried calls to dependencies (user-service, product-service, rabbitmq).",
)


def count_retry(dependency: str) -> Callable[[RetryCallState], None]:
    """A tenacity ``before_sleep`` callback that counts each retry of a dependency call."""

    def before_sleep(_: RetryCallState) -> None:
        DEPENDENCY_RETRIES.add(1, {"dependency": dependency})

    return before_sleep
