from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor

import uptrace

upclient = uptrace.Client(
    # Copy DSN here or use UPTRACE_DSN env var.
    dsn="",
    service_name="myservice",
    service_version="1.0.0",
)

Psycopg2Instrumentor().instrument()
DjangoInstrumentor().instrument()
