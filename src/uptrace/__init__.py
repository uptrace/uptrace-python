"""Uptrace exporter for OpenTelemetry"""

from .client import Client
from .version import __version__

__all__ = ["Client", "__version__"]
