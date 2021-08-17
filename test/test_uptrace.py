from unittest.mock import patch

import pytest
from opentelemetry import trace as trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.trace.status import StatusCode

import uptrace


def setup_function():
    trace._TRACER_PROVIDER = TracerProvider()


def teardown_function():
    trace._TRACER_PROVIDER = None


def test_span_processor_no_dsn(caplog):
    uptrace.configure_opentelemetry()
    assert "either dsn option or UPTRACE_DSN is required" in caplog.text


def test_span_processor_invalid_dsn(caplog):
    uptrace.configure_opentelemetry(dsn="invalid")
    assert "can't parse DSN=invalid" in caplog.text


def test_trace_url():
    uptrace.configure_opentelemetry(dsn="https://token@api.uptrace.dev/123")
    tracer = trace.get_tracer("tracer_name")
    span = tracer.start_span("main span")

    url = uptrace.trace_url(span)
    assert url.startswith("https://uptrace.dev/search/123?q=")
