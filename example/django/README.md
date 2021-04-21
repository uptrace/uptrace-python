# Instrumenting Django with OpenTelemetry

## Quickstart

Install Django
[instrumentation](https://github.com/open-telemetry/opentelemetry-python-contrib/tree/main/instrumentation/opentelemetry-instrumentation-django):

```bash
pip install opentelemetry-instrumentation-django
```

Edit `manage.py`:

```python
from opentelemetry.instrumentation.django import DjangoInstrumentor

if __name__ == "__main__":
    # DjangoInstrumentor uses DJANGO_SETTINGS_MODULE to instrument the app. Make sure to define it.
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app_name.settings")

    # Instrument the app by adding middleware etc.
    DjangoInstrumentor().instrument()

    ...
```

## Example

Install dependencies:

```shell
pip install -r requirements.txt
```

Run Django app:

```shell
UPTRACE_DSN="https://<token>@api.uptrace.dev/<project_id>" ./manage.py runserver
```

Open http://localhost:8000
