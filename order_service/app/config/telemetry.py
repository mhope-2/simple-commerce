"""OpenTelemetry setup for the order service.

FastAPI's native telemetry (``FastAPI(telemetry=...)``) traces requests, records the
HTTP server metrics and exports traces, metrics and logs over OTLP when
``OTEL_EXPORTER_OTLP_ENDPOINT`` is set. It does not instrument outgoing calls, so this
module adds instrumentation for the libraries the order flow goes through, which
propagates the trace to the user and product services and into RabbitMQ messages.
"""

from collections.abc import MutableMapping
from typing import Any

from fastapi.telemetry import TelemetryConfig
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.pika import PikaInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from sqlalchemy.ext.asyncio import AsyncEngine

# Paths that only serve the API docs; they would add noise to traces and metrics.
EXCLUDED_PATHS = frozenset({"/docs", "/docs/oauth2-redirect", "/redoc", "/openapi.json"})


def exclude_from_telemetry(scope: MutableMapping[str, Any]) -> bool:
    return scope.get("path") in EXCLUDED_PATHS


TELEMETRY: TelemetryConfig = {"exclude": exclude_from_telemetry}


def instrument_libraries(engine: AsyncEngine) -> None:
    """Instrument outgoing HTTP calls, database queries and RabbitMQ publishing.

    The instrumentations use the global providers, which FastAPI sets up from the
    environment at startup, so this can run at import time.
    """
    HTTPXClientInstrumentor().instrument()
    SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)
    PikaInstrumentor().instrument()
