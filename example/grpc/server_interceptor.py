from contextlib import contextmanager

import grpc

from opentelemetry import trace
from opentelemetry.context import attach, detach
from opentelemetry.propagate import extract
from opentelemetry.propagators.textmap import DictGetter
from opentelemetry.trace.status import Status, StatusCode


class OpenTelemetryServerInterceptor(grpc.ServerInterceptor):
    def __init__(self, tracer):
        self._tracer = tracer
        self._carrier_getter = DictGetter()

    @contextmanager
    def _set_remote_context(self, servicer_context):
        metadata = servicer_context.invocation_metadata()
        if metadata:
            md_dict = {md.key: md.value for md in metadata}
            ctx = extract(self._carrier_getter, md_dict)
            token = attach(ctx)
            try:
                yield
            finally:
                detach(token)
        else:
            yield

    def _start_span(self, handler_call_details, context):
        attributes = {
            "rpc.system": "grpc",
            "rpc.grpc.status_code": grpc.StatusCode.OK.value[0],
        }

        if handler_call_details.method:
            service, method = handler_call_details.method.lstrip("/").split("/", 1)
            attributes.update({"rpc.method": method, "rpc.service": service})

        metadata = dict(context.invocation_metadata())
        if "user-agent" in metadata:
            attributes["rpc.user_agent"] = metadata["user-agent"]

        try:
            ip, port = context.peer().split(",")[0].split(":", 1)[1].rsplit(":", 1)
            attributes.update({"net.peer.ip": ip, "net.peer.port": port})

            if ip in ("[::1]", "127.0.0.1"):
                attributes["net.peer.name"] = "localhost"

        except IndexError:
            logger.warning("Failed to parse peer address '%s'", context.peer())

        return self._tracer.start_as_current_span(
            name=handler_call_details.method,
            kind=trace.SpanKind.SERVER,
            attributes=attributes,
        )

    def intercept_service(self, continuation, handler_call_details):
        def telemetry_wrapper(behavior, request_streaming, response_streaming):
            def telemetry_interceptor(request_or_iterator, context):

                # handle streaming responses specially
                if response_streaming:
                    return self._intercept_server_stream(
                        behavior,
                        handler_call_details,
                        request_or_iterator,
                        context,
                    )

                with self._set_remote_context(context):
                    with self._start_span(handler_call_details, context) as span:
                        context = _OpenTelemetryServicerContext(context, span)

                        try:
                            return behavior(request_or_iterator, context)

                        except Exception as error:
                            if type(error) != Exception:
                                span.record_exception(error)
                            raise error

            return telemetry_interceptor

        return _wrap_rpc_behavior(continuation(handler_call_details), telemetry_wrapper)

    def _intercept_server_stream(
        self, behavior, handler_call_details, request_or_iterator, context
    ):

        with self._set_remote_context(context):
            with self._start_span(handler_call_details, context) as span:
                context = _OpenTelemetryServicerContext(context, span)

                try:
                    yield from behavior(request_or_iterator, context)

                except Exception as error:
                    # pylint:disable=unidiomatic-typecheck
                    if type(error) != Exception:
                        span.record_exception(error)
                    raise error


def _wrap_rpc_behavior(handler, continuation):
    if handler is None:
        return None

    if handler.request_streaming and handler.response_streaming:
        behavior_fn = handler.stream_stream
        handler_factory = grpc.stream_stream_rpc_method_handler
    elif handler.request_streaming and not handler.response_streaming:
        behavior_fn = handler.stream_unary
        handler_factory = grpc.stream_unary_rpc_method_handler
    elif not handler.request_streaming and handler.response_streaming:
        behavior_fn = handler.unary_stream
        handler_factory = grpc.unary_stream_rpc_method_handler
    else:
        behavior_fn = handler.unary_unary
        handler_factory = grpc.unary_unary_rpc_method_handler

    return handler_factory(
        continuation(
            behavior_fn, handler.request_streaming, handler.response_streaming
        ),
        request_deserializer=handler.request_deserializer,
        response_serializer=handler.response_serializer,
    )
