# Instrumenting Flask and uWSGI with OpenTelemetry

This example demonstrates how to use uWSGI post-fork hook to initialize OpenTelemetry. See
[documentation](https://uptrace.dev/docs/python.html#application-servers) for details.

Install dependencies:

```shell
pip install -r requirements.txt
```

Run Flask app using uWSGI:

```shell
UPTRACE_DSN="https://<token>@uptrace.dev/<project_id>" uwsgi --http=:8000 --wsgi-file=main.py --callable=application --master --enable-threads
```

Open http://localhost:8000

For more details, see
[Instrumenting Flask with OpenTelemetry](https://uptrace.dev/opentelemetry/instrumentations/python-flask.html)
