#!/usr/bin/env python3

import time
import random
import threading

import uptrace
from opentelemetry import _metrics
from opentelemetry._metrics.measurement import Measurement

meter = _metrics.get_meter("github.com/uptrace/uptrace-python")


def counter():
    counter = meter.create_counter(name="some.prefix.counter", description="TODO")

    while True:
        counter.add(1)
        time.sleep(1)


def up_down_counter():
    counter = meter.create_up_down_counter(
        name="some.prefix.up_down_counter", description="TODO"
    )

    while True:
        if random.random() >= 0.5:
            counter.add(+1)
        else:
            counter.add(-1)
        time.sleep(1)


def histogram():
    histogram = meter.create_histogram(
        name="some.prefix.histogram",
        description="TODO",
        unit="microseconds",
    )

    while True:
        histogram.record(random.randint(1, 5000000), attributes={"attr1": "value1"})
        time.sleep(1)


def counter_observer():
    number = 0

    def callback():
        nonlocal number
        number += 1
        return [Measurement(int(number))]

    counter = meter.create_observable_counter(
        name="some.prefix.counter_observer", callback=callback, description="TODO"
    )


def up_down_counter_observer():
    def callback():
        return [Measurement(random.random())]

    counter = meter.create_observable_up_down_counter(
        name="some.prefix.up_down_counter_observer",
        callback=callback,
        description="TODO",
    )


def gauge_observer():
    def callback():
        return [Measurement(random.random())]

    gauge = meter.create_observable_gauge(
        name="some.prefix.gauge_observer",
        callback=callback,
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
