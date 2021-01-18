#!/usr/bin/env python3

from flask import Flask
import uptrace
from opentelemetry import trace
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.instrumentation.flask import FlaskInstrumentor

from models import User
from exts import db

upclient = uptrace.Client(dsn="")

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()


@app.route("/ping")
def ping():
    return "pong"


@app.route("/hello/<int:user_id>")
def hello(user_id):
    span = upclient.get_current_span()

    user = db.session.query(User).filter_by(id=user_id).first()
    if user is None:
        user = User(name='', username='anonim')

    trace_url = upclient.trace_url(span)
    template = '<html><h1>Hello %s.</h1><p><a href="%s">%s</a></p></html>'
    return template % (user.username, trace_url, trace_url)


def register_extensions(app):
    db.init_app(app)

    with app.app_context():
        db.create_all()
        user = User(name='', username='admin')
        db.session.add(user)
        db.session.commit()

    trace.set_tracer_provider(TracerProvider())

    with app.app_context():
        engine = db.engine
        SQLAlchemyInstrumentor().instrument(
            engine=engine,
            service="service-A",
        )


if __name__ == "__main__":
    register_extensions(app)

    app.run(debug=True, host='0.0.0.0', port=8000)

    # Flush and close the client.
    upclient.close()
