import random
import time

from opentelemetry.sdk.trace.id_generator import IdGenerator

class UptraceIdGenerator(IdGenerator):
    def generate_span_id(self) -> int:
        high = int(time.time() * 1e3) & 0xffff_ffff
        low = random.getrandbits(32)
        return (high << 32) | low

    def generate_trace_id(self) -> int:
        high = int(time.time() * 1e9)
        low = random.getrandbits(64)
        return (high << 64) | low
