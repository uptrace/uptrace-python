"""Uptrace client config"""

import os
from urllib.parse import urlparse


# pylint:disable=too-few-public-methods
class Config:
    """Uptrace client config"""

    def __init__(self, dsn="", disabled=False, filters=None, **_kwargs):
        self.disabled = disabled

        if filters is None:
            filters = []
        self.filters = filters

        if self.disabled:
            return

        if not dsn:
            dsn = os.getenv("UPTRACE_DSN")
            if not dsn:
                raise ValueError("UPTRACE_DSN is empty or missing"+
                                 " (to disable Uptrace, pass disabled=True)")

        o = urlparse(dsn)  # pylint:disable=invalid-name
        if not o.scheme:
            raise ValueError(f"uptrace: can't parse DSN: {dsn}")

        host = o.hostname
        if o.port:
            host += f":{o.port}"

        self.dsn = o
        self.endpoint = f"{o.scheme}://{host}/api/v1/tracing{o.path}/spans"
        self.headers = {
            "Authorization": "Bearer " + o.username,
            "Content-Type": "application/msgpack",
            "Content-Encoding": "lz4",
        }
