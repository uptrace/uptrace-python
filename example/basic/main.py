#!/usr/bin/env python3

import uptrace
from opentelemetry import trace

# Configure OpenTelemetry with sensible defaults.
uptrace.configure_opentelemetry(
    # Set dsn or UPTRACE_DSN env var.
    dsn="",
    service_name="myservice",
    service_version="1.0.0",
)

# Create a tracer. Usually, tracer is a global variable.
tracer = trace.get_tracer("app_or_package_name", "1.0.0")

# Create a root span (a trace) to measure some operation.
with tracer.start_as_current_span("main-operation") as main:
    with tracer.start_as_current_span("child1-of-main") as child1:
        child1.set_attribute("key1", "value1")
        child1.record_exception(ValueError("error1"))

    with tracer.start_as_current_span("child2-of-main") as child2:
        child2.set_attribute("key2", "value2")
        child2.set_attribute("key3", 123.456)

    print("trace:", uptrace.trace_url(main))

# Send buffered spans and free resources.
uptrace.shutdown()
