from unittest.mock import MagicMock

import pytest
from opentelemetry import trace as trace_api
from opentelemetry.trace import SpanKind
from opentelemetry.trace.status import StatusCode

import uptrace


def setup_function():
    trace_api._TRACER_PROVIDER = None


def teardown_function():
    trace_api._TRACER_PROVIDER = None


def test_span_processor_no_dsn(caplog):
    uptrace.Client()
    assert " UPTRACE_DSN is empty or missing" in caplog.text


def test_span_processor_disabled():
    client = uptrace.Client(disabled=True)
    client.report_exception(ValueError("hello"))
    client.close()


def test_span_processor_invalid_dsn():
    with pytest.raises(ValueError) as excinfo:
        uptrace.Client(dsn="invalid")
    assert "uptrace: can't parse DSN: invalid" in str(excinfo.value)


def test_trace_url():
    client = uptrace.Client(dsn="https://token@api.uptrace.dev/123")
    tracer = client.get_tracer("tracer_name")
    span = tracer.start_span("main span")

    url = client.trace_url(span)
    assert url.startswith("https://uptrace.dev/123/search?q=")


def test_send():
    client = uptrace.Client(dsn="https://<token>@api.uptrace.dev/<project_id>")
    client._exporter._send = MagicMock()

    client.report_exception(ValueError("hello"))
    client.close()

    client._exporter._send.assert_called()
    traces = client._exporter._send.call_args[0][0]
    assert len(traces) == 1, traces

    trace = traces[0]
    spans = trace["spans"]
    assert len(spans) == 1
    span = spans[0]

    assert span["kind"] == SpanKind.INTERNAL.value
    assert span["statusCode"] == "unset"

    assert type(span["startTime"]) is int
    assert type(span["endTime"]) is int

    assert span["resource"] == {
        "telemetry.sdk.language": "python",
        "telemetry.sdk.name": "opentelemetry",
        "telemetry.sdk.version": "0.16b1",
    }

    events = span["events"]
    assert len(events) == 1

    event = events[0]
    attrs = event["attrs"]
    assert attrs["exception.type"] == "ValueError"
    assert attrs["exception.message"] == "hello"
    assert attrs["exception.stacktrace"] == "NoneType: None\n"
