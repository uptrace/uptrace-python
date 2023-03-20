# Instrumenting Pyramid with OpenTelemetry

Install dependencies:

```shell
pip install -r requirements.txt
```

Run Pyramid app:

```shell
UPTRACE_DSN="https://<token>@uptrace.dev/<project_id>" python3 main.py
```

Open http://localhost:6543

For more details, see
[Instrumenting Pyramid with OpenTelemetry](https://uptrace.dev/opentelemetry/instrumentations/python-pyramid.html)
