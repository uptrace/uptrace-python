"""Uptrace span exporter for OpenTelemetry"""

from .exporter import Exporter, span_processor

__all__ = ["Exporter", "span_processor"]
