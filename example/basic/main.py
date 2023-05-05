#!/usr/bin/env python3

import logging

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
    with tracer.start_as_current_span("GET /posts/:id") as child1:
        child1.set_attribute("http.method", "GET")
        child1.set_attribute("http.route", "/posts/:id")
        child1.set_attribute("http.url", "http://localhost:8080/posts/123")
        child1.set_attribute("http.status_code", 200)
        child1.record_exception(ValueError("error1"))

    with tracer.start_as_current_span("SELECT") as child2:
        child2.set_attribute("db.system", "mysql")
        child2.set_attribute("db.statement", "SELECT * FROM posts LIMIT 100")

    logging.error("Jackdaws love my big sphinx of quartz.")

    print("trace:", uptrace.trace_url(main))

# Send buffered spans and free resources.
uptrace.shutdown()
