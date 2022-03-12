import uptrace

bind = "127.0.0.1:8000"

# Sample Worker processes
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Sample logging
errorlog = "-"
loglevel = "info"
accesslog = "-"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'


def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

    uptrace.configure_opentelemetry(
        # Set dsn or UPTRACE_DSN env var.
        dsn="",
        service_name="app_or_service_name",
        service_version="1.0.0",
    )
