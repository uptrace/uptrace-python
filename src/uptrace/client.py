"""Uptrace client for Python"""

import typing
from typing import Optional

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchExportSpanProcessor

from .config import Config
from .spanexp import Exporter

DUMMY_SPAN_NAME = "__dummy__"


class Client:
    """Uptrace client for Python"""

    def __init__(self, **kwargs):
        self._cfg = Config(**kwargs)

        self._exporter = Exporter(self._cfg)
        self._bsp = BatchExportSpanProcessor(
            self._exporter,
            max_queue_size=1000,
            max_export_batch_size=1000,
            schedule_delay_millis=5000,
        )

        if self._cfg.disabled:
            self._tracer = trace.DefaultTracer()
            return

        provider = TracerProvider(resource=self._cfg.resource)
        provider.add_span_processor(self._bsp)

        trace.set_tracer_provider(provider)

        self._tracer = trace.get_tracer("uptrace-python")

    def close(self) -> None:
        """Closes the client releasing associated resources"""
        self._bsp.shutdown()

    def add_span_filter(self, filter_fn: typing.Callable):
        """Adds a filter function that filters span data"""
        self._cfg.filters.append(filter_fn)

    def report_exception(self, exc: Exception) -> None:
        """Reports an exception as a span event creating a dummy span if necessary."""

        span = trace.get_current_span()
        if span.is_recording():
            span.record_exception(exc)
            return

        span = self._tracer.start_span(DUMMY_SPAN_NAME)
        span.record_exception(exc)
        span.end()

    def trace_url(self, span: Optional[trace.Span] = None) -> str:
        """Returns the trace URL for the span."""

        if span is None:
            span = trace.get_current_span()

        dsn = self._cfg.dsn
        host = dsn.host[len("api.") :]
        trace_id = span.get_span_context().trace_id
        return f"{dsn.scheme}://{host}/search/{dsn.project_id}?q={trace_id:x}"
