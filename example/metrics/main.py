#!/usr/bin/env python3

import time

import uptrace
from opentelemetry import _metrics

# Configure OpenTelemetry with sensible defaults.
uptrace.configure_opentelemetry(
    # Set dsn or UPTRACE_DSN env var.
    dsn="",
    service_name="myservice",
    service_version="1.0.0",
)

meter = _metrics.get_meter("github.com/uptrace/uptrace-python")
counter = meter.create_counter("first_counter")

while True:
    print("increment 1")
    counter.add(1)
    time.sleep(1)
