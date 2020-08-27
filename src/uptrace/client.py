import typing

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchExportSpanProcessor

from .trace import Exporter


dummy_span_name = "__dummy__"


class Client:
    def __init__(self, **cfg):
        self._cfg = cfg

        if "filters" not in cfg:
            cfg["filters"] = []
        if "filter" in cfg:
            cfg["filters"].append(cfg["filter"])

        exporter = Exporter(**cfg)
        self._bsp = BatchExportSpanProcessor(
            exporter, max_queue_size=10000, max_export_batch_size=10000
        )

        provider = TracerProvider()
        provider.add_span_processor(self._bsp)

        trace.set_tracer_provider(provider)

        self._tracer = self.get_tracer("github.com/uptrace/uptrace-python")

    def close(self) -> None:
        self._bsp.shutdown()

    def add_filter(self, filter_fn: typing.Callable):
        self._cfg["filters"].append(filter_fn)

    def get_tracer(self, *args, **kwargs) -> "Tracer":  # pylint:disable=no-self-use
        return trace.get_tracer(*args, **kwargs)

    def get_current_span(self) -> "trace.Span":
        return trace.get_current_span()

    def report_exception(self, exc: Exception) -> None:
        """Reports an exception as a span event creating a dummy span if necessary."""

        span = self.get_current_span()
        if span.is_recording_events():
            span.record_exception(exc)
            return

        span = self._tracer.start_span(dummy_span_name)
        span.record_exception(exc)
        span.end()
