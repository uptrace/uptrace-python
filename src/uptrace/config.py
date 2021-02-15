"""Uptrace client config"""

import logging
import os
from collections import namedtuple
from typing import Optional
from urllib.parse import urlparse

from opentelemetry.sdk.resources import Attributes, Resource

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
        resource_attributes: Optional[Attributes] = None,
        resource: Optional[Resource] = None,
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

        self.resource = build_resource(
            resource, resource_attributes, service_name, service_version
        )

        if not dsn:
            dsn = os.getenv("UPTRACE_DSN", "")

        try:
            self.dsn = parse_dsn(dsn)
        except ValueError as exc:
            msg = remove_prefix(str(exc), "uptrace: ")
            # pylint:disable=logging-not-lazy
            logger.warning("Uptrace is disabled: %s", msg)

            self.disabled = True
            self.dsn = parse_dsn("https://<token>@api.uptrace.dev/<project_id>")

        dsno = self.dsn
        self.endpoint = (
            f"{dsno.scheme}://{dsno.host}/api/v1/tracing/{dsno.project_id}/spans"
        )
        self.headers = {
            "Authorization": "Bearer " + self.dsn.token,
            "Content-Type": "application/msgpack",
            "Content-Encoding": "lz4",
        }


DSN = namedtuple("DSN", ["scheme", "host", "project_id", "token"])


def parse_dsn(dsn: str) -> DSN:
    if dsn == "":
        raise ValueError("uptrace: either dsn option or UPTRACE_DSN is required")

    o = urlparse(dsn)
    if not o.scheme:
        raise ValueError(f"uptrace: can't parse DSN: {dsn}")

    host = o.hostname
    if not host:
        raise ValueError(f"uptrace: DSN does not have host (DSN={dsn})")

    if o.port:
        host += f":{o.port}"

    return DSN(
        scheme=o.scheme,
        host=host,
        project_id=remove_prefix(o.path, "/"),
        token=o.username,
    )


def build_resource(
    resource: Resource,
    resource_attributes: Attributes,
    service_name: str,
    service_version: str,
) -> Resource:
    attrs = {}

    if resource_attributes:
        attrs.update(resource_attributes)
    if service_name:
        attrs["service.name"] = service_name
    if service_version:
        attrs["service.version"] = service_version

    if resource is None:
        return Resource.create(attrs)

    if len(attrs) == 0:
        return resource

    return resource.merge(Resource.create(attrs))


def remove_prefix(s: str, prefix: str) -> str:
    return s[len(prefix) :] if s.startswith(prefix) else s
