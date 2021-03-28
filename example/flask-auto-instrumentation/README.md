# Auto-instrumenting Flask with OpenTelemetry

## Example

Install dependencies:

```shell
pip install -r requirements.txt
```

Run Flask app:

```shell
UPTRACE_DSN="https://<token>@api.uptrace.dev/<project_id>" opentelemetry-instrument python3 main.py
```

Open http://localhost:8000

## How it works?

uptrace-python registers an OpenTelemetry distro using an entry point in [setup.cfg](/setup.cfg).
`opentelemetry-instrument` utility is reponsible for loading all installed distros before running
your app.

When possible you should prefer using explicit instrumentation. For example, auto-instrumentation
does not work with Flask in debug mode.
