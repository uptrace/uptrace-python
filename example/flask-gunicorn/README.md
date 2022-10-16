# Instrumenting Flask and Gunicorn with OpenTelemetry

This example demonstrates how to use Gunicorn post-fork hook to initialize OpenTelemetry. See
[documentation](https://uptrace.dev/docs/python.html#application-servers) for details.

Install dependencies:

```shell
pip install -r requirements.txt
```

Run Flask app using Gunicorn:

```shell
UPTRACE_DSN="https://<token>@uptrace.dev/<project_id>" gunicorn main -c gunicorn.config.py
```

Open http://localhost:8000

For more details, see
[Instrumenting Flask with OpenTelemetry](https://uptrace.dev/opentelemetry/instrumentations/python-flask.html)
