#!/usr/bin/env python3

import os
import time

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
from opentelemetry.sdk.resources import Resource

dsn = os.environ.get("UPTRACE_DSN")
print("using DSN:", dsn)

temporality_delta = {
    sdkmetrics.Counter: AggregationTemporality.DELTA,
    sdkmetrics.UpDownCounter: AggregationTemporality.DELTA,
    sdkmetrics.Histogram: AggregationTemporality.DELTA,
    sdkmetrics.ObservableCounter: AggregationTemporality.DELTA,
    sdkmetrics.ObservableUpDownCounter: AggregationTemporality.DELTA,
    sdkmetrics.ObservableGauge: AggregationTemporality.DELTA,
}

exporter = OTLPMetricExporter(
    endpoint="otlp.uptrace.dev:4317",
    headers=(("uptrace-dsn", dsn),),
    timeout=5,
    compression=grpc.Compression.Gzip,
    preferred_temporality=temporality_delta,
)
reader = PeriodicExportingMetricReader(exporter)

resource = Resource(
    attributes={"service.name": "myservice", "service.version": "1.0.0"}
)
provider = MeterProvider(metric_readers=[reader], resource=resource)
metrics.set_meter_provider(provider)

meter = metrics.get_meter("github.com/uptrace/uptrace-python", "1.0.0")
counter = meter.create_counter("some.prefix.counter", description="TODO")

while True:
    counter.add(1)
    time.sleep(1)
