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

    print("trace:", uptrace.trace_url(main))

# Send buffered spans and free resources.
uptrace.shutdown()
```

## Links

- [Examples](example)
- [Documentation](https://uptrace.dev/get/opentelemetry-python.html)
- [OpenTelemetry instrumentations](https://uptrace.dev/opentelemetry/instrumentations/?lang=python)
- [OpenTelemetry Django](https://uptrace.dev/opentelemetry/instrumentations/python-django.html)
- [OpenTelemetry Flask](https://uptrace.dev/opentelemetry/instrumentations/python-flask.html)
- [OpenTelemetry FastAPI](https://uptrace.dev/opentelemetry/instrumentations/python-fastapi.html)
- [OpenTelemetry SQLAlchemy](https://uptrace.dev/opentelemetry/instrumentations/python-sqlalchemy.html)
