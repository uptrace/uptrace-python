#!/usr/bin/env python3

import os

import grpc
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.sdk.extension.aws.trace import AwsXRayIdGenerator

dsn = os.environ.get("UPTRACE_DSN")
print("using DSN:", dsn)

resource = Resource(
    attributes={"service.name": "myservice", "service.version": "1.0.0"}
)
tracer_provider = TracerProvider(
    resource=resource,
    id_generator=AwsXRayIdGenerator(),
)
trace.set_tracer_provider(tracer_provider)

exporter = OTLPSpanExporter(
    endpoint="otlp.uptrace.dev:4317",
    # Set the Uptrace dsn here or use UPTRACE_DSN env var.
    headers=(("uptrace-dsn", dsn),),
    timeout=5,
    compression=grpc.Compression.Gzip,
)

span_processor = BatchSpanProcessor(
    exporter,
    max_queue_size=1000,
    max_export_batch_size=1000,
)
tracer_provider.add_span_processor(span_processor)

tracer = trace.get_tracer("app_or_package_name", "1.0.0")

with tracer.start_as_current_span("main") as span:
    trace_id = span.get_span_context().trace_id
    print(f"trace id: {trace_id:0{32}x}")

# Send buffered spans.
trace.get_tracer_provider().shutdown()
