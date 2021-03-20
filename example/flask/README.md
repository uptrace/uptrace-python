# Instrumenting Flask with OpenTelemetry

Install dependencies:

```shell
pip install -r requirements.txt
```

Run Flask app:

```shell
UPTRACE_DSN="https://<token>@api.uptrace.dev/<project_id>" ./main.py
```

Open http://localhost:8000
