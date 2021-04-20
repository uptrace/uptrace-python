#!/usr/bin/env python3

import uptrace

uptrace.configure_opentelemetry(
    # Set dsn or UPTRACE_DSN env var.
    dsn="",
)

# Create a tracer.

from opentelemetry import trace

tracer = trace.get_tracer("app_or_package_name", "1.0.0")

# Start a span and set some attributes.

with tracer.start_as_current_span("main", kind=trace.SpanKind.SERVER) as span:
    if span.is_recording():
        span.set_attribute("key1", "value1")
        span.set_attributes({"key2": 123.456, "key3": [1, 2, 3]})

        span.add_event(
            "log",
            {
                "log.severity": "error",
                "log.message": "User not found",
                "enduser.id": "123",
            },
        )

    try:
        raise ValueError("error1")
    except ValueError as exc:
        span.record_exception(exc)
        span.set_status(trace.Status(trace.StatusCode.ERROR, str(exc)))

# Current span logic.

with tracer.start_as_current_span("main") as main:
    if trace.get_current_span() == main:
        print("main is active")

    with tracer.start_as_current_span("child") as child:
        if trace.get_current_span() == child:
            print("child is active")

    if trace.get_current_span() == main:
        print("main is active again")

# Start a span and activate it manually.

main = tracer.start_span("main", kind=trace.SpanKind.CLIENT)

with trace.use_span(main, end_on_exit=True):
    if trace.get_current_span() == main:
        print("main is active (manually)")
