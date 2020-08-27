import pytest
import uptrace


def test_span_processor_no_dsn():
    with pytest.raises(ValueError):
        uptrace.Client()


def test_span_processor_disabled():
    uptrace.Client(disabled=True)


def test_span_processor_invalid_dsn():
    with pytest.raises(ValueError) as excinfo:
        uptrace.Client(dsn="invalid")
    assert "can't parse dsn: invalid" in str(excinfo.value)
