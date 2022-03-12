#!/usr/bin/env python3

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
import uptrace

application = Flask(__name__)
FlaskInstrumentor().instrument_app(application)

application.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
db = SQLAlchemy(application)
SQLAlchemyInstrumentor().instrument(engine=db.engine)


@application.route("/")
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


@application.route("/hello/<username>")
def hello(username):
    with db.engine.connect() as conn:
        result = conn.execute(text("select 'hello world'"))
        print(result.all())

    trace_url = uptrace.trace_url()
    return f"""
<html>
  <h3>Hello {username}</h3>
  <p><a href="{trace_url}">{trace_url}</a></p>
</html>
"""


if __name__ == "__main__":
    application.run()

    # Send buffered spans.
    trace.get_tracer_provider().shutdown()
