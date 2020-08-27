#!/usr/bin/env python3

import uptrace

# Set dsn or UPTRACE_DSN env var.
client = uptrace.Client(dsn="")
tracer = client.get_tracer(__name__)

with tracer.start_as_current_span("main span"):
    with tracer.start_as_current_span("child1") as span:
        span.set_attribute("key1", "value1")
        span.add_event(
            "log",
            {
                "log.severity": "error",
                "log.message": "User not found",
                "enduser.id": "123",
            },
        )

    with tracer.start_as_current_span("child2") as span:
        span.set_attribute("key2", "value2")
        span.add_event(
            "log",
            {
                "log.severity": "error",
                "log.message": "User not found",
                "enduser.id": "321",
            },
        )

client.close()
