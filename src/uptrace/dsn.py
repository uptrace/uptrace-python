from collections import namedtuple
from urllib.parse import urlparse

from .util import remove_prefix

DSN = namedtuple("DSN", ["str", "scheme", "host", "project_id", "token"])


def parse_dsn(dsn: str) -> DSN:
    if dsn == "":
        raise ValueError("either dsn option or UPTRACE_DSN is required")

    o = urlparse(dsn)
    if not o.scheme:
        raise ValueError(f"can't parse DSN={dsn}")

    host = o.hostname
    if not host:
        raise ValueError(f"DSN={dsn} does not have a host")

    if o.port:
        host += f":{o.port}"

    project_id = remove_prefix(o.path, "/")
    if not project_id:
        raise ValueError(f"DSN={dsn} does not have a project id")

    token = o.username
    if not token:
        raise ValueError(f"DSN={dsn} does not have a token")

    return DSN(
        str=dsn,
        scheme=o.scheme,
        host=host,
        project_id=project_id,
        token=token,
    )
