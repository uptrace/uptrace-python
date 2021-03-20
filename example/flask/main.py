#!/usr/bin/env python3

from flask import Flask
from markupsafe import escape
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor

import uptrace

uptrace.configure_opentelemetry(
    # Set dsn or UPTRACE_DSN env var.
    dsn="",
)

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)


@app.route("/")
def index():
    trace_url = uptrace.trace_url()

    return f"""
<html>
  <p>Here are some routes for you:</p>

  <ul>
    <li><a href="/hello/world">Hello world</a></li>
    <li><a href="/hello/foo-bar">Hello foo-bar</a></li>
  </ul>

  <p><a href="{trace_url}">{trace_url}</a></p>
</html>
"""


@app.route("/hello/<username>")
def hello(username):
    trace_url = uptrace.trace_url()
    return f"""
<html>
  <h3>Hello {username}</h3>
  <p><a href="{trace_url}">{trace_url}</a></p>
</html>
"""


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)

    # Send buffered spans.
    trace.get_tracer_provider().shutdown()
