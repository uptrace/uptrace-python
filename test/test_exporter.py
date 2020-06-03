import pytest
import uptrace


def test_span_processor_no_dsn():
    with pytest.raises(ValueError):
        uptrace.trace.span_processor()


def test_span_processor_disabled():
    uptrace.trace.span_processor(disabled=True)


def test_span_processor_invalid_dsn():
    with pytest.raises(ValueError):
        uptrace.trace.span_processor(dsn="invalid")
