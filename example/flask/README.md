# Instrumenting Flask with OpenTelemetry

## Quickstart

Install Flask
[instrumentation](https://github.com/open-telemetry/opentelemetry-python-contrib/tree/main/instrumentation/opentelemetry-instrumentation-flask):

```bash
pip install opentelemetry-instrumentation-flask
```

Then edit the file where you create a Flask app:

```python
from opentelemetry.instrumentation.flask import FlaskInstrumentor

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
```

## Example

Install dependencies:

```shell
pip install -r requirements.txt
```

Run Flask app:

```shell
UPTRACE_DSN="https://<token>@api.uptrace.dev/<project_id>" ./main.py
```

Open http://localhost:8000
