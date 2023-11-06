import logging
import os
from socket import gethostname
from typing import Optional

from opentelemetry import _logs, metrics, trace
from opentelemetry.sdk.resources import Attributes, Resource

from .client import Client
from .dsn import parse_dsn
from .logs import configure_logs
from .metrics import configure_metrics
from .traces import configure_traces

logger = logging.getLogger(__name__)

_CLIENT = Client(parse_dsn("https://<token>@api.uptrace.dev"))


# pylint: disable=too-many-arguments
def configure_opentelemetry(
    dsn="",
    service_name: Optional[str] = "",
    service_version: Optional[str] = "",
    deployment_environment: Optional[str] = "",
    resource_attributes: Optional[Attributes] = None,
    resource: Optional[Resource] = None,
    logging_level=logging.NOTSET,
):
    """
    configure_opentelemetry configures OpenTelemetry to export data to Uptrace.
    By default it:
       - Creates tracer provider.
       - Registers OTLP span exporter.
       - Creates metrics provider.
       - Registers OTLP metrics exporter.
    """

    global _CLIENT  # pylint: disable=global-statement

    if os.getenv("UPTRACE_DISABLED") == "True":
        logger.info("UPTRACE_DISABLED=True: Uptrace is disabled")
        return

    if not dsn:
        dsn = os.getenv("UPTRACE_DSN", "")

    try:
        dsn = parse_dsn(dsn)
    except ValueError as exc:
        # pylint:disable=logging-not-lazy
        logger.warning("can't parse Uptrace DSN: %s (Uptrace is disabled)", exc)
        return

    if dsn.token == "<token>":
        logger.warning("dummy Uptrace DSN detected: %s (Uptrace is disabled)", dsn)
        return

    if dsn.grpc_port == "14318":
        logger.warning(
            "uptrace-python uses OTLP/gRPC exporter, but got port %s", dsn.port
        )

    resource = _build_resource(
        resource,
        resource_attributes,
        service_name,
        service_version,
        deployment_environment,
    )

    _CLIENT = Client(dsn=dsn)
    configure_traces(dsn, resource=resource)
    configure_metrics(dsn, resource=resource)
    configure_logs(dsn, resource=resource, level=logging_level)


def shutdown():
    trace.get_tracer_provider().shutdown()
    metrics.get_meter_provider().shutdown()
    _logs.get_logger_provider().shutdown()


def force_flush():
    trace.get_tracer_provider().force_flush()
    metrics.get_meter_provider().force_flush()
    _logs.get_logger_provider().force_flush()


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
    deployment_environment: str,
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
    if deployment_environment:
        attrs["deployment.environment"] = deployment_environment

    return Resource.create(attrs)
