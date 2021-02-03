#!/usr/bin/env python3

import uptrace

# Set dsn or UPTRACE_DSN env var.
upclient = uptrace.Client(dsn="")

# Use upclient to report errors when there are no spans.
upclient.report_exception(ValueError("Hello from uptrace-python"))

tracer = upclient.get_tracer(__name__)

with tracer.start_as_current_span("main span") as span:
    with tracer.start_as_current_span("child1") as span:
        span.set_attribute("key1", "value1")
        span.record_exception(ValueError("exception1"))

    with tracer.start_as_current_span("child2") as span:
        span.set_attribute("key2", "value2")
        span.set_attribute("key3", 123.456)

    print("trace:", upclient.trace_url(span))

# Flush and close the client.
upclient.close()
