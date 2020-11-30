"""Uptrace client config"""

import logging
import os
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# pylint:disable=too-few-public-methods
class Config:
    """Uptrace client config"""

    def __init__(self, dsn="", disabled=False, filters=None, **_kwargs):
        self.disabled = disabled
        if os.getenv("UPTRACE_DISABLED") == "True":
            self.disabled = True

        if filters is None:
            filters = []
        self.filters = filters

        if self.disabled:
            return

        if not dsn:
            dsn = os.getenv("UPTRACE_DSN")
            if not dsn:
                # pylint:disable=logging-not-lazy
                logger.warning(
                    "uptrace: UPTRACE_DSN is empty or missing"
                    + " (to hide this message, use UPTRACE_DISABLED=True)"
                )
                self.disabled = True
                return

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
