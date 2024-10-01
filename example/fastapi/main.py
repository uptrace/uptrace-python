#!/usr/bin/env python3

from typing import Optional

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
import uptrace

app = FastAPI()

uptrace.configure_opentelemetry(
    # Copy DSN here or use UPTRACE_DSN env var.
    # dsn="",
    service_name="server_name",
    service_version="1.0.0",
)
FastAPIInstrumentor.instrument_app(app)


@app.get("/")
def read_root():
    span = trace.get_current_span()
    return {"Hello": "World", "trace_url": uptrace.trace_url(span)}


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Optional[str] = None):
    span = trace.get_current_span()
    return {"item_id": item_id, "q": q, "trace_url": uptrace.trace_url(span)}
