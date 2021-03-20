"""Uptrace span exporter for OpenTelemetry"""

import logging
import typing
from types import MappingProxyType

import msgpack
import requests
import zstd
from opentelemetry.sdk import trace as trace_sdk
from opentelemetry.sdk.trace import export as sdk
from opentelemetry.sdk.util import BoundedDict
from opentelemetry.trace import Link, SpanKind
from opentelemetry.trace.status import StatusCode

from ..dsn import DSN

logger = logging.getLogger(__name__)


class Exporter(sdk.SpanExporter):  # pylint:disable=too-many-instance-attributes
    """Uptrace span exporter for OpenTelemetry."""

    def __init__(self, dsn: DSN):
        self._dsn = dsn
        self._closed = False

        self._endpoint = (
            f"{dsn.scheme}://{dsn.host}/api/v1/tracing/{dsn.project_id}/spans"
        )
        self._headers = {
            "Authorization": "Bearer " + dsn.token,
            "Content-Type": "application/msgpack",
            "Content-Encoding": "zstd",
        }

    def export(self, spans: typing.Sequence[sdk.Span]) -> sdk.SpanExportResult:
        if self._closed:
            return sdk.SpanExportResult.SUCCESS

        spans_out = []

        for span in spans:
            out = _out_span(span)
            spans_out.append(out)

        self._send(spans_out)

        return sdk.SpanExportResult.SUCCESS

    def shutdown(self) -> None:
        if self._closed:
            return
        self._closed = True

    def _send(self, spans):
        payload = msgpack.packb({"spans": spans})
        payload = zstd.compress(payload)

        resp = requests.post(self._endpoint, data=payload, headers=self._headers)
        if resp.status_code < 200 or resp.status_code >= 300:
            logger.error("uptrace: status=%d %s", resp.status_code, resp.text)


def _out_span(span: sdk.Span):
    out = {
        "id": span.context.span_id,
        "traceId": _trace_id_bytes(span.context.trace_id),
        "name": span.name,
        "kind": _kind(span.kind),
        "startTime": span.start_time,
        "endTime": span.end_time,
    }

    if span.parent is not None:
        out["parentId"] = span.parent.span_id

    out["statusCode"] = _status(span.status.status_code)
    if span.status.description:
        out["statusMessage"] = span.status.description

    out["tracerName"] = span.instrumentation_info.name
    if span.instrumentation_info.version:
        out["tracerVersion"] = span.instrumentation_info.version

    if span.attributes:
        out["attrs"] = _attrs(span.attributes)

    if span.events:
        out["events"] = _events(span.events)

    if span.links:
        out["links"] = _links(span.links)

    if span.resource:
        out["resource"] = _attrs(span.resource.attributes)

    return out


def _events(events: typing.Sequence[trace_sdk.Event]):
    out = []
    for event in events:
        out.append(
            {
                "name": event.name,
                "attrs": _attrs(event.attributes),
                "time": event.timestamp,
            }
        )
    return out


def _links(links: typing.Sequence[Link]):
    out = []
    for link in links:
        out.append(
            {
                "traceId": _trace_id_bytes(link.context.trace_id),
                "spanId": link.context.span_id,
                "attrs": _attrs(link.attributes),
            }
        )
    return out


def _kind(kind: SpanKind) -> str:
    if kind == SpanKind.SERVER:
        return "server"
    if kind == SpanKind.CLIENT:
        return "client"
    if kind == SpanKind.PRODUCER:
        return "producer"
    if kind == SpanKind.CONSUMER:
        return "consumer"
    return "internal"


def _status(status: StatusCode) -> str:
    if status == StatusCode.ERROR:
        return "error"
    if status == StatusCode.OK:
        return "ok"
    return "unset"


def _attrs(attrs):
    if isinstance(attrs, BoundedDict):
        return attrs._dict  # pylint: disable=protected-access
    if isinstance(attrs, MappingProxyType):
        return dict(attrs)
    return attrs


def _trace_id_bytes(trace_id: int):
    return trace_id.to_bytes(16, byteorder="big")
