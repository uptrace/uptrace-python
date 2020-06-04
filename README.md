# Uptrace Python exporter for OpenTelemetry

[![Build Status](https://travis-ci.org/uptrace/uptrace-python.svg?branch=master)](https://travis-ci.org/uptrace/uptrace-python)

## Installation

```bash
pip install uptrace
```

## Introduction

uptrace-go is an exporter for [OpenTelemetry](https://opentelemetry.io/) that
sends your traces/spans and metrics to [Uptrace.dev](https://uptrace.dev).
Briefly the process is the following:

- OpenTelemetry API is used to instrument your application with spans and
  metrics.
- OpenTelemetry SDK and this exporter send collected information to Uptrace.dev.
- Uptrace.dev uses that information to help you pinpoint failures and find
  performance bottlenecks.

## Instrumenting code

You instrument your application by wrapping potentially interesting operations
with spans. Each span has:

- an operation name;
- a start time and end time;
- a set of key/value attributes containing data about the operation;
- a set of timed events representing events, errors, logs, etc.

You create spans using a tracer:

```python
from opentelemetry.trace import get_tracer

# Create a named tracer using your module name as an identifier.
tracer = get_tracer(__name__, __version__)
```

To create a span and set it as the current span:

```python
with tracer.start_as_current_span("operation-name") as span:
    do_some_work()
```

Alternatively you can use `start_span` which does roughly the same:

```python
span = tracer.start_span(name)
with tracer.use_span(span, end_on_exit=True):
    do_some_work()
```

To get an existing span from the tracer context:

```python
span = tracer.get_current_span()
```

Once you have a span you can start adding attributes:

```python
span.set_attribute("enduser.id", "123")
span.set_attribute("enduser.role", "admin")
```

or events:

```python
span.add_event("log", {
    "log.severity": "error",
    "log.message": "User not found",
    "enduser.id": "123",
})
```

## Span exporter

Span exporter exports spans to Uptrace.dev backend. To configure span exporter
add the following code to your main file (for Django it is manage.py):

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
import uptrace

# The preferred tracer implementation must be set, as the opentelemetry-api
# defines the interface with a no-op implementation.
trace.set_tracer_provider(TracerProvider())

trace.get_tracer_provider().add_span_processor(uptrace.trace.span_processor(
    dsn=""  # copy your project DSN here or use UPTRACE_DSN env var
))
```

## Instrumenting Django

Install Django instrumentation extension:

```bash
pip install opentelemetry-ext-django
```

Set environment variables:

```bash
# Enable instrumentation.
export OPENTELEMETRY_PYTHON_DJANGO_INSTRUMENT=True

# Django settings that will be used to install OpenTelemetry middleware.
export DJANGO_SETTINGS_MODULE=app_name.settings
```

Edit `manage.py`:

```python
from opentelemetry.ext.django import DjangoInstrumentor

if __name__ == "__main__":
    # Instrument Django by adding middleware etc.
    DjangoInstrumentor().instrument()

    ...
```

Run the server:

```bash
export OPENTELEMETRY_PYTHON_DJANGO_INSTRUMENT=True
export DJANGO_SETTINGS_MODULE=app_name.settings

./manage.py runserver
```

## Instrumenting PostgreSQL psycopg2

Install psycopg instrumentation extension:

```bash
pip install opentelemetry-ext-psycopg2
```

Update your main file (for Django it is manage.py):

```python
from opentelemetry.ext.psycopg2 import Psycopg2Instrumentor

if __name__ == "__main__":
    Psycopg2Instrumentor().instrument()

    ...
```
