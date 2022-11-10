# Instrumenting Django with OpenTelemetry

## Example

Install dependencies:

```shell
pip install -r requirements.txt
```

Run Django app:

```shell
UPTRACE_DSN="https://<token>@uptrace.dev/<project_id>" ./manage.py runserver
```

And open http://127.0.0.1:8000

For more details, see
[Instrumenting Django with OpenTelemetry](https://uptrace.dev/opentelemetry/instrumentations/python-django.html)
