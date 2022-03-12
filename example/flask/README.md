# Instrumenting Flask with OpenTelemetry

Install dependencies:

```shell
pip install -r requirements.txt
```

Run Flask app:

```shell
UPTRACE_DSN="https://<key>@uptrace.dev/<project_id>" ./main.py
```

Open http://localhost:8000

For more details, see
[Instrumenting Flask with OpenTelemetry](https://opentelemetry.uptrace.dev/instrumentations/python-flask.html)
