from unittest.mock import patch

import pytest
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import InMemoryMetricReader

from app.schemas.order import OrderMessage, OrderMessagePayload, OrderPayload
from app.services.order import publish_message

# The business metrics use the global meter provider; give this test run one we can read.
reader = InMemoryMetricReader()
metrics.set_meter_provider(MeterProvider(metric_readers=[reader]))


def counter_values(name: str) -> dict[tuple, int]:
    """Current value of each data point of a counter, keyed by its sorted attributes."""
    values: dict[tuple, int] = {}
    data = reader.get_metrics_data()
    for rm in data.resource_metrics if data else []:
        for sm in rm.scope_metrics:
            for metric in sm.metrics:
                if metric.name == name:
                    for point in metric.data.data_points:
                        values[tuple(sorted(point.attributes.items()))] = point.value
    return values


def message() -> OrderMessage:
    return OrderMessage(
        producer="order_service",
        sent_at="2026-01-01T00:00:00+00:00",
        type="created_order",
        payload=OrderMessagePayload(
            order=OrderPayload(
                order_id="1", customer_full_name="John Doe", product_name="Product 1",
                total_amount=9.99, created_at="2026-01-01T00:00:00+00:00",
            )
        ),
    )


def test_order_created_and_failed_counters(test_client, mock_fetch_user, mock_fetch_product, mock_publish_message):
    before = counter_values("orders.created").get((("product.code", "product1"),), 0)
    res = test_client.post("/orders/", json={"user_id": "7c11e1ce2741", "product_code": "product1", "quantity": 1})
    assert res.status_code == 200
    assert counter_values("orders.created")[(("product.code", "product1"),)] == before + 1


def test_order_failed_counter(test_client, mock_fetch_user_not_found):
    before = counter_values("orders.failed").get((("error.type", "404"),), 0)
    res = test_client.post("/orders/", json={"user_id": "unknown", "product_code": "product1", "quantity": 1})
    assert res.status_code == 404
    assert counter_values("orders.failed")[(("error.type", "404"),)] == before + 1


def test_publish_success_counter():
    before = counter_values("orders.messages.published").get((("outcome", "success"),), 0)
    with patch("app.services.order._publish") as publish:
        publish_message(message())
    publish.assert_called_once()
    assert counter_values("orders.messages.published")[(("outcome", "success"),)] == before + 1


def test_publish_failure_and_retry_counters():
    failures = counter_values("orders.messages.published").get((("outcome", "failure"),), 0)
    retries = counter_values("orders.dependency.retries").get((("dependency", "rabbitmq"),), 0)
    with (
        patch("app.services.order.Producer.publish", side_effect=ConnectionError("down")),
        patch("tenacity.nap.time.sleep"),
        pytest.raises(Exception),
    ):
        publish_message(message())
    assert counter_values("orders.messages.published")[(("outcome", "failure"),)] == failures + 1
    # Three attempts, so two retries.
    assert counter_values("orders.dependency.retries")[(("dependency", "rabbitmq"),)] == retries + 2
