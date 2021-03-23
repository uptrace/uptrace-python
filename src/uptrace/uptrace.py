import logging
import os
from typing import Optional

from opentelemetry import trace

from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchExportSpanProcessor
from opentelemetry.sdk.resources import Attributes, Resource
from opentelemetry.propagators import set_global_textmap
from opentelemetry.propagators.composite import CompositeHTTPPropagator
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.trace.propagation.textmap import TextMapPropagator
from opentelemetry.baggage.propagation import BaggagePropagator

from .client import Client
from .dsn import parse_dsn, DSN
from .spanexp import Exporter

logger = logging.getLogger(__name__)

_CLIENT = None
_FALLBACK_CLIENT = Client(parse_dsn("https://<token>@api.uptrace.dev/<project_id>"))

# pylint: disable=too-many-arguments
def configure_opentelemetry(
    dsn="",
    service_name: Optional[str] = "",
    service_version: Optional[str] = "",
    resource_attributes: Optional[Attributes] = None,
    resource: Optional[Resource] = None,
    text_map_propagator: Optional[TextMapPropagator] = None,
):
    """
    configureOpentelemetry configures OpenTelemetry to export data to Uptrace.
    By default it:
       - creates tracer provider;
       - registers Uptrace span exporter;
       - sets tracecontext + baggage composite context propagator.
    """

    global _CLIENT  # pylint: disable=global-statement

    if os.getenv("UPTRACE_DISABLED") == "True":
        return

    if _CLIENT is not None:
        logger.warning("Uptrace is already configured")

    if not dsn:
        dsn = os.getenv("UPTRACE_DSN", "")

    try:
        dsn = parse_dsn(dsn)
    except ValueError as exc:
        # pylint:disable=logging-not-lazy
        logger.warning("Uptrace is disabled: %s", exc)
        return

    _CLIENT = Client(dsn=dsn)
    _configure_tracing(
        dsn,
        service_name=service_name,
        service_version=service_version,
        resource_attributes=resource_attributes,
        resource=resource,
    )
    _configure_propagator(text_map_propagator=text_map_propagator)


def _configure_tracing(
    dsn: DSN,
    service_name: Optional[str] = "",
    service_version: Optional[str] = "",
    resource_attributes: Optional[Attributes] = None,
    resource: Optional[Resource] = None,
):
    if trace._TRACER_PROVIDER is None:
        resource = _build_resource(
            resource, resource_attributes, service_name, service_version
        )
        provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(provider)

    exporter = Exporter(dsn)
    bsp = BatchExportSpanProcessor(
        exporter,
        max_queue_size=1000,
        max_export_batch_size=1000,
        schedule_delay_millis=5000,
    )
    trace.get_tracer_provider().add_span_processor(bsp)


def _configure_propagator(text_map_propagator: Optional[TextMapPropagator] = None):
    if text_map_propagator is None:
        text_map_propagator = CompositeHTTPPropagator(
            [TraceContextTextMapPropagator(), BaggagePropagator()]
        )
    set_global_textmap(text_map_propagator)


def trace_url(span: Optional[trace.Span] = None) -> str:
    """Returns the trace URL for the span."""

    if _CLIENT is not None:
        return _CLIENT.trace_url(span)

    return _FALLBACK_CLIENT.trace_url(span)


def report_exception(exc: Exception) -> None:
    if _CLIENT is not None:
        _CLIENT.report_exception(exc)


def _build_resource(
    resource: Resource,
    resource_attributes: Attributes,
    service_name: str,
    service_version: str,
) -> Resource:
    attrs = {}

    if resource_attributes:
        attrs.update(resource_attributes)
    if service_name:
        attrs["service.name"] = service_name
    if service_version:
        attrs["service.version"] = service_version

    if resource is None:
        return Resource.create(attrs)

    if len(attrs) == 0:
        return resource

    return resource.merge(Resource.create(attrs))
