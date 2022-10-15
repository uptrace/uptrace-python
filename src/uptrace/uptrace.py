import logging
import os
from socket import gethostname
from typing import Optional

import grpc
from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
    OTLPMetricExporter,
)
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.sdk import metrics as sdkmetrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    AggregationTemporality,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.resources import Attributes, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from .client import Client
from .dsn import DSN, parse_dsn

logger = logging.getLogger(__name__)

_CLIENT = Client(parse_dsn("https://<token>@uptrace.dev/<project_id>"))

temporality_delta = {
    sdkmetrics.Counter: AggregationTemporality.DELTA,
    sdkmetrics.UpDownCounter: AggregationTemporality.DELTA,
    sdkmetrics.Histogram: AggregationTemporality.DELTA,
    sdkmetrics.ObservableCounter: AggregationTemporality.DELTA,
    sdkmetrics.ObservableUpDownCounter: AggregationTemporality.DELTA,
    sdkmetrics.ObservableGauge: AggregationTemporality.DELTA,
}

# pylint: disable=too-many-arguments
def configure_opentelemetry(
    dsn="",
    service_name: Optional[str] = "",
    service_version: Optional[str] = "",
    resource_attributes: Optional[Attributes] = None,
    resource: Optional[Resource] = None,
):
    """
    configure_opentelemetry configures OpenTelemetry to export data to Uptrace.
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
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    credentials = grpc.ssl_channel_credentials()
    exporter = OTLPSpanExporter(
        endpoint=dsn.otlp_grpc_addr,
        credentials=credentials,
        headers=(("uptrace-dsn", dsn.str),),
        timeout=5,
        compression=grpc.Compression.Gzip,
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
        preferred_temporality=temporality_delta,
    )
    reader = PeriodicExportingMetricReader(exporter)
    provider = MeterProvider(metric_readers=[reader], resource=resource)
    metrics.set_meter_provider(provider)


def shutdown():
    trace.get_tracer_provider().shutdown()


def force_flush():
    trace.get_tracer_provider().force_flush()
    metrics.get_meter_provider().force_flush()


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
