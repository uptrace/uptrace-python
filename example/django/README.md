# Instrumenting Django with OpenTelemetry

Install dependencies:

```shell
pip install -r requirements.txt
```

Run Django app:

```shell
UPTRACE_DSN="https://<token>@api.uptrace.dev/<project_id>" OTEL_PYTHON_TRACER_PROVIDER=sdk_tracer_provider ./manage.py runserver
```

Open http://localhost:8000
