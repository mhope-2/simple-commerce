from collections.abc import MutableMapping
from typing import Any

from fastapi.telemetry import TelemetryConfig

# Paths that only serve the API docs; they would add noise to traces and metrics.
EXCLUDED_PATHS = frozenset({"/docs", "/docs/oauth2-redirect", "/redoc", "/openapi.json"})


def exclude_from_telemetry(scope: MutableMapping[str, Any]) -> bool:
    return scope.get("path") in EXCLUDED_PATHS


# FastAPI's native OpenTelemetry support. Traces, metrics and logs are exported over
# OTLP when OTEL_EXPORTER_OTLP_ENDPOINT is set (see docker-compose.yml); the service
# name comes from OTEL_SERVICE_NAME.
TELEMETRY: TelemetryConfig = {"exclude": exclude_from_telemetry}
