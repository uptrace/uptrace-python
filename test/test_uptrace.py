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
    tracer = trace.get_tracer("tracer_name")
    span = tracer.start_span("main span")

    url = uptrace.trace_url(span)
    assert url.startswith("https://app.uptrace.dev/traces/")


def test_dsn():
    dsn = uptrace.parse_dsn("http://localhost:14318")
    assert dsn.site_url == "http://localhost:14318"
    assert dsn.otlp_http_endpoint == "http://localhost:14318"
    assert dsn.otlp_grpc_endpoint == "http://localhost:14317"

    dsn = uptrace.parse_dsn("https://localhost?grpc=123")
    assert dsn.site_url == "https://localhost"
    assert dsn.otlp_http_endpoint == "https://localhost"
    assert dsn.otlp_grpc_endpoint == "https://localhost:123"

    dsn = uptrace.parse_dsn("https://<token>@uptrace.dev/<project_id>")
    assert dsn.site_url == "https://app.uptrace.dev"
    assert dsn.otlp_http_endpoint == "https://otlp.uptrace.dev"
    assert dsn.otlp_grpc_endpoint == "https://otlp.uptrace.dev:4317"
