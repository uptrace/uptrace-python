from concurrent import futures
import logging

import grpc
import helloworld_pb2
import helloworld_pb2_grpc

from server_interceptor import OpenTelemetryServerInterceptor

import uptrace

# remove
logger = logging.getLogger(__name__)

upclient = uptrace.Client(dsn="")


class Greeter(helloworld_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        span = upclient.get_current_span()

        trace_url = upclient.trace_url(span)
        return helloworld_pb2.HelloReply(
            message="Hello, %s. %s" % [request.name, trace_url]
        )


def serve():
    tracer = upclient.get_tracer(__name__)

    interceptors = [
        OpenTelemetryServerInterceptor(tracer),
    ]
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        interceptors=interceptors,
    )
    helloworld_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig()

    serve()
