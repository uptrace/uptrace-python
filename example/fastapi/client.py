#!/usr/bin/env python3

import requests
from opentelemetry import trace
from opentelemetry.instrumentation.requests import RequestsInstrumentor
import uptrace

uptrace.configure_opentelemetry(
    # Copy DSN here or use UPTRACE_DSN env var.
    # dsn="",
    service_name="client_name",
    service_version="1.0.0",
)
RequestsInstrumentor().instrument()

tracer = trace.get_tracer("app_or_package_name", "1.0.0")

with tracer.start_as_current_span("main-operation") as main:
    resp = requests.get("http://127.0.0.1:8000/items/5?q=somequery")
    print(resp)
    print(uptrace.trace_url())
