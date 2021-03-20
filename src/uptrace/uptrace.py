import logging
import os
from typing import Optional

from opentelemetry import trace
from opentelemetry.sdk.trace.export import BatchExportSpanProcessor

from .client import Client
from .dsn import parse_dsn
from .spanexp import Exporter

logger = logging.getLogger(__name__)

_CLIENT = None
_FALLBACK_CLIENT = Client(parse_dsn("https://<token>@api.uptrace.dev/<project_id>"))

# pylint: disable=too-many-arguments
def configure_opentelemetry(
    dsn="",
):
    global _CLIENT  # pylint: disable=global-statement

    if os.getenv("UPTRACE_DISABLED") == "True":
        return

    if _CLIENT is not None:
        logger.warning("Uptrace is already configured")

    if not dsn:
        dsn = os.getenv("UPTRACE_DSN", "")

    try:
        dsn = parse_dsn(dsn)
    except ValueError as exc:
        # pylint:disable=logging-not-lazy
        logger.warning("Uptrace is disabled: %s", exc)
        return

    exporter = Exporter(dsn)
    bsp = BatchExportSpanProcessor(
        exporter,
        max_queue_size=1000,
        max_export_batch_size=1000,
        schedule_delay_millis=5000,
    )
    trace.get_tracer_provider().add_span_processor(bsp)

    _CLIENT = Client(dsn=dsn)


def trace_url(span: Optional[trace.Span] = None) -> str:
    """Returns the trace URL for the span."""

    if _CLIENT is not None:
        return _CLIENT.trace_url(span)

    return _FALLBACK_CLIENT.trace_url(span)


def report_exception(exc: Exception) -> None:
    if _CLIENT is not None:
        _CLIENT.report_exception(exc)
