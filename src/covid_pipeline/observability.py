"""Structured logging and request correlation for Cloud Run."""
from __future__ import annotations

import json
import logging
import os
import sys
import time
import uuid
from typing import Any

from flask import g, request


class JsonFormatter(logging.Formatter):
    """Emit Cloud Logging-friendly JSON records."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "severity": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "timestamp": self.formatTime(record, self.datefmt),
            "service": os.getenv("K_SERVICE", "covid-pipeline"),
            "revision": os.getenv("K_REVISION", "local"),
            "version": os.getenv("APP_VERSION", "unknown"),
        }
        request_id = getattr(record, "request_id", None)
        if request_id:
            payload["request_id"] = request_id
        for key in ("event_id", "source_object", "rows_loaded", "duration_ms"):
            value = getattr(record, key, None)
            if value is not None:
                payload[key] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging() -> None:
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(getattr(logging, level, logging.INFO))


def register_request_logging(app) -> None:
    @app.before_request
    def _before_request() -> None:
        g.request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        g.request_started = time.perf_counter()

    @app.after_request
    def _after_request(response):
        duration_ms = round((time.perf_counter() - g.request_started) * 1000, 2)
        response.headers["X-Request-ID"] = g.request_id
        logging.getLogger("coviddataops.http").info(
            "HTTP request completed",
            extra={"request_id": g.request_id, "duration_ms": duration_ms},
        )
        return response
