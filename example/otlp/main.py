#!/usr/bin/env python3

# https://opentelemetry-python.readthedocs.io/en/latest/exporter/otlp/otlp.html

import os

import grpc
from opentelemetry import trace
from opentelemetry.exporter.otlp.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchExportSpanProcessor


resource = Resource(
    attributes={"service.name": "myservice", "service.version": "1.0.0"}
)
tracer_provider = TracerProvider(resource=resource)

# Load system credentials.
credentials = grpc.ssl_channel_credentials()
otlp_exporter = OTLPSpanExporter(
    endpoint="otlp.uptrace.dev:4317",
    credentials=credentials,
    headers=(("uptrace-token", os.environ.get("UPTRACE_TOKEN")),),
)

span_processor = BatchExportSpanProcessor(otlp_exporter)
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
    print(f"trace id: {trace_id:x}")

# Flush the buffers.
span_processor.shutdown()
