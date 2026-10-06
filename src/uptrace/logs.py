import logging

import grpc
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import (
    OTLPLogExporter,
)
from opentelemetry.instrumentation.logging.handler import LoggingHandler
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource

from .dsn import DSN


def configure_logs(dsn: DSN, resource: Resource, level=logging.NOTSET):
    logger_provider = LoggerProvider(resource=resource)
    set_logger_provider(logger_provider)

    exporter = OTLPLogExporter(
        endpoint=dsn.otlp_grpc_endpoint,
        headers=(("uptrace-dsn", dsn.str),),
        timeout=5,
        compression=grpc.Compression.Gzip,
    )
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))

    handler = LoggingHandler(
        level=level, logger_provider=logger_provider, log_code_attributes=True
    )
    logging.getLogger().addHandler(handler)
