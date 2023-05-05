# Configuring OTLP traces exporter for Uptrace

This example shows how to configure
[OTLP](https://opentelemetry-python.readthedocs.io/en/latest/exporter/otlp/otlp.html) to export
traces to Uptrace.

Install dependencies:

```shell
pip install -r requirements.txt
```

Run:

```go
UPTRACE_DSN=https://<token>@api.uptrace.dev/<project_id> ./main.py
```
