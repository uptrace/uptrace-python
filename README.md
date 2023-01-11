# Uptrace for Python

![build workflow](https://github.com/uptrace/uptrace-python/actions/workflows/build.yml/badge.svg)
[![Documentation](https://img.shields.io/badge/uptrace-documentation-informational)](https://uptrace.dev/get/opentelemetry-python.html)
[![Chat](https://img.shields.io/badge/-telegram-red?color=white&logo=telegram&logoColor=black)](https://t.me/uptrace)

<a href="https://uptrace.dev/get/opentelemetry-python.html">
  <img src="https://uptrace.dev/get/devicon/python-original.svg" height="200px" />
</a>

## Introduction

uptrace-python is an OpenTelemery distribution configured to export
[traces](https://uptrace.dev/opentelemetry/distributed-tracing.html) and
[metrics](https://uptrace.dev/opentelemetry/metrics.html) to Uptrace.

## Quickstart

Install uptrace-python:

```bash
pip install uptrace
```

Run the [basic example](example/basic) below using the DSN from the Uptrace project settings page.

```python
#!/usr/bin/env python3

import uptrace
from opentelemetry import trace

# Set dsn or UPTRACE_DSN env var.
uptrace.configure_opentelemetry(
    dsn="", service_name="myservice", service_version="1.0.0"
)
tracer = trace.get_tracer("app_or_package_name", "1.0.0")

with tracer.start_as_current_span("main") as span:
    with tracer.start_as_current_span("child1") as span:
        span.set_attribute("key1", "value1")
        span.record_exception(ValueError("error1"))

    with tracer.start_as_current_span("child2") as span:
        span.set_attribute("key2", "value2")
        span.set_attribute("key3", 123.456)

    print("trace:", uptrace.trace_url(span))

# Send buffered spans.
trace.get_tracer_provider().shutdown()
```

## Links

- [Examples](example)
- [Documentation](https://uptrace.dev/get/opentelemetry-python.html)
- [OpenTelemetry instrumentations](https://uptrace.dev/opentelemetry/instrumentations/?lang=python)
- [OpenTelemetry Django](https://uptrace.dev/opentelemetry/instrumentations/python-django.html)
- [OpenTelemetry Flask](https://uptrace.dev/opentelemetry/instrumentations/python-flask.html)
- [OpenTelemetry FastAPI](https://uptrace.dev/opentelemetry/instrumentations/python-fastapi.html)
- [OpenTelemetry SQLAlchemy](https://uptrace.dev/opentelemetry/instrumentations/python-sqlalchemy.html)
