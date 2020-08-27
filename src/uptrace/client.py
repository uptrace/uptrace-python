import typing

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.trace import get_tracer
from opentelemetry.sdk.trace.export import BatchExportSpanProcessor

from .trace import Exporter


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

    def add_filter(self, fn: typing.Callable):
        self._cfg["filters"].append(fn)

    def close(self) -> None:
        self._bsp.shutdown()

    def get_tracer(self, *args, **kwargs) -> "Tracer":
        return get_tracer(*args, **kwargs)
