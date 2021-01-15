#!/usr/bin/env python3

from flask import Flask
from markupsafe import escape
import uptrace
from opentelemetry.instrumentation.flask import FlaskInstrumentor

upclient = uptrace.Client(dsn="")

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)


@app.route("/ping")
def ping():
    return "pong"


@app.route("/hello/<username>")
def hello(username):
    span = upclient.get_current_span()

    trace_url = upclient.trace_url(span)
    template = '<html><h1>Hello %s.</h1><p><a href="%s">%s</a></p></html>'
    return template % (escape(username), trace_url, trace_url)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000)

    # Flush and close the client.
    upclient.close()
