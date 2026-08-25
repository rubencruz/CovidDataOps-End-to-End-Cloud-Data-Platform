"""HTTP entry point for the COVID data pipeline on Cloud Run.

Phase 3 exposes /ingest for explicit authenticated HTTP invocation.
Phase 4 adds /events/pubsub for Eventarc -> Pub/Sub -> Cloud Run events.
"""
from __future__ import annotations

import logging
from typing import Any

from flask import Flask, g, jsonify, request

from covid_pipeline.events.pubsub_handler import handle_pubsub_event
from covid_pipeline.ingestion.config import BUCKET_NAME
from covid_pipeline.jobs.quality_check import run_quality_check
from covid_pipeline.jobs.reconciliation import run_reconciliation
from covid_pipeline.main import run
from covid_pipeline.observability import configure_logging, register_request_logging

LOGGER = logging.getLogger("coviddataops")
app = Flask(__name__)
configure_logging()
register_request_logging(app)


@app.get("/health")
def health():
    return jsonify({"status": "ok"}), 200


@app.post("/ingest")
def ingest():
    """Trigger ingestion explicitly from an authenticated HTTP request."""
    try:
        payload = request.get_json(silent=True) or {}
        bucket = payload.get("bucket") or BUCKET_NAME
        source = payload.get("object") or payload.get("source")

        if not source:
            return jsonify({"status": "error", "message": "Missing required field: object"}), 400

        rows_loaded = run(source=source, bucket=bucket)
        return jsonify({
            "status": "success",
            "bucket": bucket,
            "object": source,
            "rows_loaded": rows_loaded,
        }), 200
    except Exception:
        LOGGER.exception("COVID-19 ingestion failed", extra={"request_id": getattr(g, "request_id", None)})
        return jsonify({"status": "error", "message": "COVID-19 ingestion failed"}), 500


@app.post("/events/pubsub")
def pubsub_event():
    """Receive an Eventarc CloudEvent backed by a Pub/Sub message."""
    try:
        event: dict[str, Any] = request.get_json(silent=True) or {}
        rows_loaded = handle_pubsub_event(event)
        return jsonify({"status": "success", "rows_loaded": rows_loaded}), 200
    except ValueError as exc:
        LOGGER.warning("Invalid Pub/Sub event: %s", exc)
        return jsonify({"status": "error", "message": str(exc)}), 400
    except Exception:
        LOGGER.exception("Event-driven COVID-19 ingestion failed")
        return jsonify({"status": "error", "message": "Event-driven ingestion failed"}), 500


@app.post("/jobs/quality-check")
def quality_check():
    """Run the scheduled BigQuery data-quality checks."""
    try:
        result = run_quality_check()
        return jsonify(result), 200
    except RuntimeError as exc:
        LOGGER.error("Quality check failed: %s", exc)
        return jsonify({"status": "failed", "message": str(exc)}), 500
    except Exception:
        LOGGER.exception("Quality check execution failed")
        return jsonify({"status": "error", "message": "Quality check execution failed"}), 500


@app.post("/jobs/reconciliation")
def reconciliation():
    """Run scheduled lineage and duplicate reconciliation checks."""
    try:
        result = run_reconciliation()
        return jsonify(result), 200
    except RuntimeError as exc:
        LOGGER.error("Reconciliation failed: %s", exc)
        return jsonify({"status": "failed", "message": str(exc)}), 500
    except Exception:
        LOGGER.exception("Reconciliation execution failed")
        return jsonify({"status": "error", "message": "Reconciliation execution failed"}), 500
