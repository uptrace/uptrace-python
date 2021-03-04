from __future__ import print_function
import logging

import grpc

import helloworld_pb2
import helloworld_pb2_grpc
from client_interceptor import OpenTelemetryClientInterceptor

upclient = uptrace.Client(dsn="")

import uptrace


class GrpcInstrumentorClient(BaseInstrumentor):
    def _which_channel(self, kwargs):
        if "channel_type" in kwargs:
            if kwargs.get("channel_type") == "secure":
                return ("secure_channel",)
            return ("insecure_channel",)

        types = []
        for ctype in ("secure_channel", "insecure_channel"):
            if kwargs.get(ctype, True):
                types.append(ctype)

        return tuple(types)

    def _instrument(self, **kwargs):
        for ctype in self._which_channel(kwargs):
            _wrap(
                "grpc", ctype, self.wrapper_fn,
            )

    def _uninstrument(self, **kwargs):
        for ctype in self._which_channel(kwargs):
            unwrap(grpc, ctype)

    def wrapper_fn(self, original_func, instance, args, kwargs):
        channel = original_func(*args, **kwargs)
        tracer_provider = kwargs.get("tracer_provider")
        return intercept_channel(
            channel, client_interceptor(tracer_provider=tracer_provider),
        )


def client_interceptor(tracer_provider=None):
    tracer = upclient.get_tracer(__name__)
    return _client.OpenTelemetryClientInterceptor(tracer)


def run():
    grpc_client_instrumentor = GrpcInstrumentorClient()
    grpc.client_instrumentor.instrument()

    with grpc.insecure_channel('localhost:50051') as channel:
        stub = helloworld_pb2_grpc.GreeterStub(channel)
        response = stub.SayHello(helloworld_pb2.HelloRequest(name='you'))
    print("Greeter client received: " + response.message)


if __name__ == '__main__':
    logging.basicConfig()
    run()
