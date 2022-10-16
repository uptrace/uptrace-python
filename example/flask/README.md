# Instrumenting Flask with OpenTelemetry

Install dependencies:

```shell
pip install -r requirements.txt
```

Run Flask app:

```shell
UPTRACE_DSN="https://<token>@uptrace.dev/<project_id>" python3 main.py
```

Open http://localhost:8000

For more details, see
[Instrumenting Flask with OpenTelemetry](https://uptrace.dev/opentelemetry/instrumentations/python-flask.html)
