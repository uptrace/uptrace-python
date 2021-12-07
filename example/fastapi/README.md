# Example for OpenTelemetry FastAPI instrumentation

Install dependencies:

```shell
pip install -r requirements.txt
```

Start the server:

```shell
UPTRACE_DSN="https://<key>@uptrace.dev/<project_id>" uvicorn main:app --reload
```

Start the client:

```shell
UPTRACE_DSN="https://<key>@uptrace.dev/<project_id>" ./client.py
```

Follow the link from console to open Uptrace.
