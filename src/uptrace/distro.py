from opentelemetry.instrumentation.distro import BaseDistro

from .uptrace import configure_opentelemetry


# pylint: disable=too-few-public-methods
class UptraceDistro(BaseDistro):
    def _configure(self, **kwargs):
        configure_opentelemetry()
