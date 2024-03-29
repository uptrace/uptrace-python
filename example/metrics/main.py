#!/usr/bin/env python3

import time
import random
import threading
from typing import Iterable

import uptrace
from opentelemetry import metrics
from opentelemetry.metrics import CallbackOptions, Observation

meter = metrics.get_meter("github.com/uptrace/uptrace-python", "1.0.0")


def counter():
    counter = meter.create_counter("some.prefix.counter", description="TODO")

    while True:
        counter.add(1)
        time.sleep(1)


def up_down_counter():
    counter = meter.create_up_down_counter(
        "some.prefix.up_down_counter", description="TODO"
    )

    while True:
        if random.random() >= 0.5:
            counter.add(+1)
        else:
            counter.add(-1)
        time.sleep(1)


def histogram():
    histogram = meter.create_histogram(
        "some.prefix.histogram",
        description="TODO",
        unit="microseconds",
    )

    while True:
        histogram.record(random.randint(1, 5000000), attributes={"attr1": "value1"})
        time.sleep(1)


def counter_observer():
    number = 0

    def callback(options: CallbackOptions) -> Iterable[Observation]:
        nonlocal number
        number += 1
        yield Observation(int(number), {})

    counter = meter.create_observable_counter(
        "some.prefix.counter_observer", [callback], description="TODO"
    )


def up_down_counter_observer():
    def callback(options: CallbackOptions) -> Iterable[Observation]:
        yield Observation(random.random(), {})

    counter = meter.create_observable_up_down_counter(
        "some.prefix.up_down_counter_observer",
        [callback],
        description="TODO",
    )


def gauge_observer():
    def callback(options: CallbackOptions) -> Iterable[Observation]:
        yield Observation(random.random(), {})

    gauge = meter.create_observable_gauge(
        "some.prefix.gauge_observer",
        [callback],
        description="TODO",
    )


def main():
    # Configure OpenTelemetry with sensible defaults.
    uptrace.configure_opentelemetry(
        # Set dsn or UPTRACE_DSN env var.
        dsn="",
        service_name="myservice",
        service_version="1.0.0",
    )

    threading.Thread(target=counter).start()
    threading.Thread(target=up_down_counter).start()
    threading.Thread(target=histogram).start()

    counter_observer()
    up_down_counter_observer()
    gauge_observer()

    print("reporting measurements to Uptrace... (press Ctrl+C to stop)")
    time.sleep(300)


if __name__ == "__main__":
    main()
