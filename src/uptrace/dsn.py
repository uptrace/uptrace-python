from urllib.parse import parse_qs, urlparse


class DSN:
    # pylint:disable=too-many-arguments
    def __init__(
        self, dsn="", scheme="", host="", http_port="", grpc_port="", token=""
    ):
        self.str = dsn
        self.scheme = scheme
        self.host = host
        self.http_port = http_port
        self.grpc_port = grpc_port
        self.token = token

    def __str__(self):
        return self.str

    @property
    def site_url(self):
        if self.host == "uptrace.dev":
            return "https://app.uptrace.dev"
        if self.http_port:
            return f"{self.scheme}://{self.host}:{self.http_port}"
        return f"{self.scheme}://{self.host}"

    @property
    def otlp_http_endpoint(self):
        if self.host == "uptrace.dev":
            return "https://otlp.uptrace.dev"
        if self.http_port:
            return f"{self.scheme}://{self.host}:{self.http_port}"
        return f"{self.scheme}://{self.host}"

    @property
    def otlp_grpc_endpoint(self):
        if self.host == "uptrace.dev":
            return "https://otlp.uptrace.dev:4317"
        if self.grpc_port:
            return f"{self.scheme}://{self.host}:{self.grpc_port}"
        return f"{self.scheme}://{self.host}"


def parse_dsn(dsn: str) -> DSN:
    if dsn == "":
        raise ValueError("either dsn option or UPTRACE_DSN is required")

    o = urlparse(dsn)
    if not o.scheme:
        raise ValueError(f"can't parse DSN={dsn}")

    host = o.hostname
    if not host:
        raise ValueError(f"DSN={dsn} does not have a host")
    if host == "api.uptrace.dev":
        host = "uptrace.dev"

    token = o.username
    grpc_port = "14317"
    if o.query:
        query = parse_qs(o.query)
        if "grpc" in query:
            grpc_port = query["grpc"][0]

    return DSN(
        dsn=dsn,
        scheme=o.scheme,
        host=host,
        http_port=o.port,
        grpc_port=grpc_port,
        token=token,
    )
