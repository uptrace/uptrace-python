#!/usr/bin/env python3

import uptrace
from flask import Flask
from opentelemetry.instrumentation.flask import FlaskInstrumentor

upclient = uptrace.Client(dsn="")
upclient.report_exception(ValueError("Hello from flask"))
tracer = upclient.get_tracer(__name__)

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)


@app.route("/")
def hello():
    tracer = upclient.get_tracer(__name__)

    with tracer.start_as_current_span("main span") as span:
        with tracer.start_as_current_span("child1") as span:
            span.set_attribute("key1", "value1")
            span.add_event("event-name", {"foo": "bar"})

        with tracer.start_as_current_span("child2") as span:
            span.set_attribute("key2", "value2")
            span.add_event("event-name", {"foo": "baz"})

    print("trace", upclient.trace_url(span))

    return "Hello!"


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000)

    # Flush and close the client.
    upclient.close()
