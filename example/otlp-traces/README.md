# Configuring OTLP traces exporter for Uptrace

This example shows how to configure
[OTLP](https://opentelemetry-python.readthedocs.io/en/latest/exporter/otlp/otlp.html) to export
traces to Uptrace.

Install dependencies:

```shell
pip install -r requirements.txt
```

To run this example, you need to
[create an Uptrace project](https://uptrace.dev/get/get-started.html) and pass your project DSN via
`UPTRACE_DSN` env variable:

```go
UPTRACE_DSN=https://<token>@api.uptrace.dev/<project_id> ./main.py
```
