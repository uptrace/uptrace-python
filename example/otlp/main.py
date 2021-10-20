#!/usr/bin/env python3

import os

from opentelemetry import trace

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http import Compression
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

dsn = os.environ.get("UPTRACE_DSN")
print("using DSN:", dsn)

resource = Resource(
    attributes={"service.name": "myservice", "service.version": "1.0.0"}
)
tracer_provider = TracerProvider(resource=resource)

# Load system TLS credentials.
otlp_exporter = OTLPSpanExporter(
    endpoint="https://otlp.uptrace.dev/v1/traces",
    # Set the Uptrace dsn here or use UPTRACE_DSN env var.
    headers=(("uptrace-dsn", dsn),),
    timeout=5,
    compression=Compression.Gzip,
)

span_processor = BatchSpanProcessor(
    otlp_exporter,
    max_queue_size=1000,
    max_export_batch_size=1000,
)
tracer_provider.add_span_processor(span_processor)

trace.set_tracer_provider(tracer_provider)

tracer = trace.get_tracer("app_or_package_name", "1.0.0")

with tracer.start_as_current_span("main") as span:
    with tracer.start_as_current_span("child1") as span:
        span.set_attribute("key1", "value1")
        span.record_exception(ValueError("error1"))

    with tracer.start_as_current_span("child2") as span:
        span.set_attribute("key2", "value2")
        span.set_attribute("key3", 123.456)

    trace_id = span.get_span_context().trace_id
    print(f"trace id: {trace_id:0{32}x}")

# Send buffered spans.
trace.get_tracer_provider().shutdown()
