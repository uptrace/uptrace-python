# gRPC instrumentation example

<!-- [![Documentation](https://img.shields.io/badge/uptrace-documentation-informational)](https://docs.uptrace.dev/python/opentelemetry-grpc/)  -->


## Running with Docker

To run this example:

```shell
UPTRACE_DSN="https://<key>@uptrace.dev/<project_id>" make
```

## Running locally

Start the server:

```shell
UPTRACE_DSN="https://<key>@uptrace.dev/<project_id>" python server/server.go
```

Start the client:

```shell
UPTRACE_DSN="https://<key>@uptrace.dev/<project_id>" python client/client.go
```

The server output should look like this:

```shell
UPTRACE_DSN="https://<key>@uptrace.dev/<project_id>" python server/server.go
serving on :9999
trace https://uptrace.dev/search/<project_id>?q=<trace_id>
```
