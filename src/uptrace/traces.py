import grpc
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from .dsn import DSN
from .id_generator import UptraceIdGenerator


def configure_traces(
    dsn: DSN,
    resource: Resource,
):
    provider = TracerProvider(resource=resource, id_generator=UptraceIdGenerator())
    trace.set_tracer_provider(provider)

    exporter = OTLPSpanExporter(
        endpoint=dsn.otlp_grpc_endpoint,
        headers=(("uptrace-dsn", dsn.str),),
        timeout=5,
        compression=grpc.Compression.Gzip,
    )

    bsp = BatchSpanProcessor(
        exporter,
        max_queue_size=1000,
        max_export_batch_size=1000,
        schedule_delay_millis=5000,
    )
    trace.get_tracer_provider().add_span_processor(bsp)
