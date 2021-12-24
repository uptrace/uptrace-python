#!/usr/bin/env python3

from typing import Optional

from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
import uptrace

app = FastAPI()

uptrace.configure_opentelemetry(
    # Copy DSN here or use UPTRACE_DSN env var.
    # dsn="",
)
FastAPIInstrumentor.instrument_app(app)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}
