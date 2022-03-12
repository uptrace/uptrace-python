# Instrumenting Django with OpenTelemetry

## Example

Install dependencies:

```shell
pip install -r requirements.txt
```

Run Django app:

```shell
UPTRACE_DSN="https://<key>@uptrace.dev/<project_id>" ./manage.py runserver
```

And open http://localhost:8000

For more details, see
[Instrumenting Django with OpenTelemetry](https://opentelemetry.uptrace.dev/instrumentations/python-django.html)
