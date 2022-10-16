# Auto-instrumenting Flask with OpenTelemetry

## Example

Install dependencies:

```shell
pip install -r requirements.txt
```

Run Flask app:

```shell
UPTRACE_DSN="https://<token>@uptrace.dev/<project_id>" opentelemetry-instrument python3 main.py
```

Open http://localhost:8000

## Documentation

See [Auto-instrumentation](http://localhost:8081/guide/python.html#auto-instrumentation)
