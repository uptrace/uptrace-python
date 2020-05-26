# Uptrace Python exporter for OpenTelemetry

## Introduction

uptrace-python is an exporter for [OpenTelemetry](https://opentelemetry.io/) that sends your traces and metrics to [Uptrace.dev](https://uptrace.dev).

## Installation

```bash
pip install uptrace
```

## Trace exporter

Trace exporter can be configured with the following code:

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchExportSpanProcessor
import uptrace

# The preferred tracer implementation must be set, as the opentelemetry-api
# defines the interface with a no-op implementation.
trace.set_tracer_provider(TracerProvider())

# Exporter receives the spans and sends them to Uptrace.dev.
exporter = uptrace.trace.Exporter(
    dsn="" # copy your project DSN here or use UPTRACE_DSN env var
)

span_processor = BatchExportSpanProcessor(
    exporter, max_queue_size=10000, max_export_batch_size=10000
)
trace.get_tracer_provider().add_span_processor(span_processor)
```
