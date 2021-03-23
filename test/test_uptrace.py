from unittest.mock import patch

import pytest
from opentelemetry import trace as trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.trace.status import StatusCode

import uptrace
from uptrace.spanexp import Exporter


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


@patch.object(Exporter, "_send")
def test_send(send):
    uptrace.configure_opentelemetry(
        dsn="https://<token>@api.uptrace.dev/<project_id>",
        service_name="myservice",
    )

    uptrace.report_exception(ValueError("hello"))
    trace.get_tracer_provider().shutdown()

    send.assert_called()
    spans = send.call_args[0][0]
    assert len(spans) == 1, traces
    span = spans[0]

    assert type(span["startTime"]) is int
    assert type(span["endTime"]) is int

    assert span["kind"] == "internal"
    assert span["statusCode"] == "unset"

    assert span["tracerName"] == "uptrace-python"

    assert span["resource"] == {
        "service.name": "unknown_service",
        "telemetry.sdk.language": "python",
        "telemetry.sdk.name": "opentelemetry",
        "telemetry.sdk.version": "1.0.0rc1",
    }

    events = span["events"]
    assert len(events) == 1

    event = events[0]
    attrs = event["attrs"]
    assert attrs["exception.type"] == "ValueError"
    assert attrs["exception.message"] == "hello"
    assert attrs["exception.stacktrace"] == "NoneType: None\n"
