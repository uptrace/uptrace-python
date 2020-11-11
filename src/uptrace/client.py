"""Uptrace client for Python"""

import typing

from opentelemetry import trace as trace_api
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchExportSpanProcessor

from .spanexp import Exporter

DUMMY_SPAN_NAME = "__dummy__"


class Client:
    """Uptrace client for Python"""

    def __init__(self, **cfg):
        self._cfg = cfg

        if "filters" not in cfg:
            cfg["filters"] = []
        if "filter" in cfg:
            cfg["filters"].append(cfg["filter"])

        self._exporter = Exporter(**cfg)
        self._bsp = BatchExportSpanProcessor(
            self._exporter, max_queue_size=10000, max_export_batch_size=10000
        )

        if self._cfg.get('disabled', False):
            self._tracer = trace_api.DefaultTracer()
            return

        provider = TracerProvider()
        provider.add_span_processor(self._bsp)

        trace_api.set_tracer_provider(provider)

        self._tracer = self.get_tracer("github.com/uptrace/uptrace-python")

    def close(self) -> None:
        """Closes the client releasing associated resources"""
        self._bsp.shutdown()

    def add_span_filter(self, filter_fn: typing.Callable):
        """Adds a filter function that filters span data"""
        self._cfg["filters"].append(filter_fn)

    def get_tracer(self, *args, **kwargs) -> "Tracer":  # pylint:disable=no-self-use
        """Shortcut for trace.get_tracer"""
        return trace_api.get_tracer(*args, **kwargs)

    def get_current_span(self) -> "trace.Span":  # pylint:disable=no-self-use
        """Shortcut for trace.get_current_span"""
        return trace_api.get_current_span()

    def report_exception(self, exc: Exception) -> None:
        """Reports an exception as a span event creating a dummy span if necessary."""

        span = self.get_current_span()
        if span.is_recording():
            span.record_exception(exc)
            return

        span = self._tracer.start_span(DUMMY_SPAN_NAME)
        span.record_exception(exc)
        span.end()
