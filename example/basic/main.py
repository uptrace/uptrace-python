#!/usr/bin/env python3

from opentelemetry import trace
import uptrace

upclient = uptrace.Client(
    # Set dsn or UPTRACE_DSN env var.
    dsn="",
    service_name="myservice",
    service_version="1.0.0",
)

# Use upclient to report errors when there are no spans.
upclient.report_exception(ValueError("Hello from uptrace-python"))

tracer = trace.get_tracer("app_or_package_name", "1.0.0")

with tracer.start_as_current_span("main") as span:
    with tracer.start_as_current_span("child1") as span:
        span.set_attribute("key1", "value1")
        span.record_exception(ValueError("error1"))

    with tracer.start_as_current_span("child2") as span:
        span.set_attribute("key2", "value2")
        span.set_attribute("key3", 123.456)

    print("trace:", upclient.trace_url(span))

# Flush and close the client.
upclient.close()
