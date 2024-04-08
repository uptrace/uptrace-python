import grpc
from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
    OTLPMetricExporter,
)
from opentelemetry.sdk import metrics as sdkmetrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    AggregationTemporality,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.metrics.view import (
    ExponentialBucketHistogramAggregation,
)
from opentelemetry.sdk.resources import Resource

from .dsn import DSN

temporality_delta = {
    sdkmetrics.Counter: AggregationTemporality.DELTA,
    sdkmetrics.UpDownCounter: AggregationTemporality.DELTA,
    sdkmetrics.Histogram: AggregationTemporality.DELTA,
    sdkmetrics.ObservableCounter: AggregationTemporality.DELTA,
    sdkmetrics.ObservableUpDownCounter: AggregationTemporality.DELTA,
    sdkmetrics.ObservableGauge: AggregationTemporality.DELTA,
}


def configure_metrics(
    dsn: DSN,
    resource: Resource,
):
    exporter = OTLPMetricExporter(
        endpoint=dsn.otlp_grpc_endpoint,
        headers=(("uptrace-dsn", dsn.str),),
        timeout=5,
        compression=grpc.Compression.Gzip,
        preferred_temporality=temporality_delta,
        preferred_aggregation={
            sdkmetrics.Histogram: ExponentialBucketHistogramAggregation()
        },
    )
    reader = PeriodicExportingMetricReader(exporter)
    provider = MeterProvider(metric_readers=[reader], resource=resource)
    metrics.set_meter_provider(provider)
