import logging
import sys

from opentelemetry import trace
from opentelemetry.sdk._logs import LoggingHandler
from pythonjsonlogger import jsonlogger


class TraceContextFilter(logging.Filter):
    """Add the current trace and span IDs to each record, so logs can be matched to traces."""

    def filter(self, record: logging.LogRecord) -> bool:
        ctx = trace.get_current_span().get_span_context()
        record.trace_id = format(ctx.trace_id, "032x") if ctx.is_valid else ""
        record.span_id = format(ctx.span_id, "016x") if ctx.is_valid else ""
        return True


def setup_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(TraceContextFilter())
    handler.setFormatter(
        jsonlogger.JsonFormatter(fmt="%(asctime)s %(name)s %(levelname)s %(message)s %(trace_id)s %(span_id)s")
    )
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(handler)
    # Also send application logs over OTLP (to Loki, via the collector). The handler uses
    # the global logger provider, which FastAPI configures from the environment at startup;
    # until then, and when no OTLP endpoint is set, records are dropped.
    root.addHandler(LoggingHandler())
