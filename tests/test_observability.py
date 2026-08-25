import json
import logging

from covid_pipeline.observability import JsonFormatter


def test_json_formatter_contains_operational_fields(monkeypatch):
    monkeypatch.setenv("APP_VERSION", "phase-7-test")
    record = logging.LogRecord("test", logging.INFO, __file__, 1, "hello", (), None)
    record.request_id = "req-123"
    record.source_object = "sample.csv"
    record.rows_loaded = 42
    payload = json.loads(JsonFormatter().format(record))
    assert payload["message"] == "hello"
    assert payload["request_id"] == "req-123"
    assert payload["source_object"] == "sample.csv"
    assert payload["rows_loaded"] == 42
    assert payload["version"] == "phase-7-test"
