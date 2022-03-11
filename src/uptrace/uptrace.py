import logging
import os
from socket import gethostname
from typing import Optional

import grpc
from opentelemetry import trace, _metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from opentelemetry.sdk._metrics import MeterProvider
from opentelemetry.sdk._metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Attributes, Resource
from opentelemetry.exporter.otlp.proto.http import Compression
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc._metric_exporter import OTLPMetricExporter

from .client import Client
from .dsn import parse_dsn, DSN

logger = logging.getLogger(__name__)

_CLIENT = Client(parse_dsn("https://<token>@uptrace.dev/<project_id>"))

# pylint: disable=too-many-arguments
def configure_opentelemetry(
    dsn="",
    service_name: Optional[str] = "",
    service_version: Optional[str] = "",
    resource_attributes: Optional[Attributes] = None,
    resource: Optional[Resource] = None,
):
    """
    configureOpentelemetry configures OpenTelemetry to export data to Uptrace.
    By default it:
       - creates tracer provider;
       - registers OTLP span exporter.
    """

    global _CLIENT  # pylint: disable=global-statement

    if os.getenv("UPTRACE_DISABLED") == "True":
        return
    if not dsn:
        dsn = os.getenv("UPTRACE_DSN", "")

    try:
        dsn = parse_dsn(dsn)
    except ValueError as exc:
        # pylint:disable=logging-not-lazy
        logger.warning("Uptrace is disabled: %s", exc)
        return

    resource = _build_resource(
        resource, resource_attributes, service_name, service_version
    )

    _CLIENT = Client(dsn=dsn)
    _configure_tracing(dsn, resource=resource)
    _configure_metrics(dsn, resource=resource)


def _configure_tracing(
    dsn: DSN,
    resource: Optional[Resource] = None,
):
    if trace._TRACER_PROVIDER is None:
        provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(provider)

    exporter = OTLPSpanExporter(
        endpoint=f"{dsn.otlp_http_addr}/v1/traces",
        headers=(("uptrace-dsn", dsn.str),),
        timeout=5,
        compression=Compression.Gzip,
    )

    bsp = BatchSpanProcessor(
        exporter,
        max_queue_size=1000,
        max_export_batch_size=1000,
        schedule_delay_millis=5000,
    )
    trace.get_tracer_provider().add_span_processor(bsp)


def _configure_metrics(
    dsn: DSN,
    resource: Optional[Resource] = None,
):
    exporter = OTLPMetricExporter(
        endpoint=f"{dsn.otlp_grpc_addr}",
        headers=(("uptrace-dsn", dsn.str),),
        timeout=5,
        compression=grpc.Compression.Gzip,
    )
    reader = PeriodicExportingMetricReader(exporter, export_interval_millis=1000)
    provider = MeterProvider(metric_readers=[reader], resource=resource)
    _metrics.set_meter_provider(provider)


def trace_url(span: Optional[trace.Span] = None) -> str:
    """Returns the trace URL for the span."""

    return _CLIENT.trace_url(span)


def report_exception(exc: Exception) -> None:
    if _CLIENT is not None:
        _CLIENT.report_exception(exc)


def _build_resource(
    resource: Resource,
    resource_attributes: Attributes,
    service_name: str,
    service_version: str,
) -> Resource:
    if resource:
        return resource

    attrs = {"host.name": gethostname()}

    if resource_attributes:
        attrs.update(resource_attributes)
    if service_name:
        attrs["service.name"] = service_name
    if service_version:
        attrs["service.version"] = service_version

    return Resource.create(attrs)
