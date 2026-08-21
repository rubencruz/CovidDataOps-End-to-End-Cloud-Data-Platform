"""HTTP entry point for the CovidDataOps Cloud Run service.

Receives a GCS bucket/object through an HTTP POST request and
triggers the Phase 2 COVID-19 ingestion pipeline.
"""

from __future__ import annotations

import logging

from flask import Flask, jsonify, request

from covid_pipeline.ingestion.config import BUCKET_NAME
from covid_pipeline.main import run

LOGGER = logging.getLogger("coviddataops")

app = Flask(__name__)


@app.get("/health")
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok"}), 200


@app.post("/ingest")
def ingest():
    """Trigger COVID-19 ingestion from a GCS object."""

    try:
        payload = request.get_json(silent=True) or {}

        bucket = payload.get("bucket") or BUCKET_NAME
        source = payload.get("object") or payload.get("source")

        if not source:
            return jsonify(
                {
                    "status": "error",
                    "message": "Missing required field: object",
                }
            ), 400

        LOGGER.info(
            "Starting ingestion: gs://%s/%s",
            bucket,
            source,
        )

        rows_loaded = run(
            source=source,
            bucket=bucket,
        )

        return jsonify(
            {
                "status": "success",
                "bucket": bucket,
                "object": source,
                "rows_loaded": rows_loaded,
            }
        ), 200

    except Exception:
        LOGGER.exception("COVID-19 ingestion failed")

        return jsonify(
            {
                "status": "error",
                "message": "COVID-19 ingestion failed",
            }
        ), 500