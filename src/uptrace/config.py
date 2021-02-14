"""Uptrace client config"""

import logging
import os
from urllib.parse import urlparse

from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, Resource

logger = logging.getLogger(__name__)

# pylint:disable=too-few-public-methods
class Config:
    """Uptrace client config"""

    # pylint:disable=too-many-arguments
    def __init__(
        self,
        dsn="",
        disabled=False,
        filters=None,
        service_name="",
        service_version="",
        resource: Resource = None,
        **_kwargs,
    ):
        self.disabled = disabled
        if os.getenv("UPTRACE_DISABLED") == "True":
            self.disabled = True

        if filters is None:
            filters = []
        self.filters = filters

        if self.disabled:
            return

        self.resource = build_resource(resource, service_name, service_version)

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


def build_resource(
    resource: Resource, service_name: str, service_version: str
) -> Resource:
    """_"""

    attrs = {}

    if service_name != "":
        attrs[SERVICE_NAME] = service_name
    if service_version != "":
        attrs[SERVICE_VERSION] = service_version

    if resource is None:
        return Resource.create(attrs)

    if len(attrs) == 0:
        return resource

    return resource.merge(Resource.create(attrs))
