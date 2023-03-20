#!/usr/bin/env python3

import time
from opentelemetry.instrumentation.pyramid import PyramidInstrumentor
from opentelemetry import trace
import uptrace
from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.view import view_config


tracer = trace.get_tracer("mypyramid", "1.0.0")


@view_config(route_name="home")
def home(request):
    with tracer.start_as_current_span("SELECT") as span:
        span.set_attribute("db.system", "postgresql")
        span.set_attribute("db.statement", "SELECT * FROM articles LIMIT 100")
        time.sleep(0.1)

    trace_url = uptrace.trace_url()
    return Response(
        f"""
<html>
  <p>Here are some routes for you:</p>

  <ul>
    <li><a href="/hello/world">Hello world</a></li>
    <li><a href="/hello/foo-bar">Hello foo-bar</a></li>
  </ul>

  <p>View trace: <a href="{trace_url}">{trace_url}</a></p>
</html>
"""
    )


@view_config(route_name="hello")
def hello(request):
    username = request.matchdict["username"]
    trace_url = uptrace.trace_url()
    return Response(
        f"""
<html>
  <h3>Hello {username}</h3>
  <p><a href="{trace_url}">{trace_url}</a></p>
</html>
"""
    )


if __name__ == "__main__":
    uptrace.configure_opentelemetry(
        # Set dsn or UPTRACE_DSN env var.
        # dsn="",
        service_name="myservice",
        service_version="1.0.0",
    )
    PyramidInstrumentor().instrument()

    with Configurator() as config:
        config.add_route("home", "/")
        config.add_route("hello", "/hello/{username}")
        config.scan()

        app = config.make_wsgi_app()

    print("listening on http://localhost:6543")
    server = make_server("0.0.0.0", 6543, app)
    server.serve_forever()
