"""HTTP entry point for the CovidDataOps Cloud Run service.

Endpoints:
    GET  /health
    POST /ingest
    POST /events/pubsub

The /events/pubsub endpoint receives CloudEvents from Eventarc,
triggered by Pub/Sub messages generated from Cloud Storage
OBJECT_FINALIZE notifications.
"""

from __future__ import annotations

import base64
import json
import logging
from urllib.parse import unquote

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
    """Trigger COVID-19 ingestion from a simple JSON payload."""

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

        return process_ingestion(bucket=bucket, source=source)

    except Exception:
        LOGGER.exception("COVID-19 ingestion failed")

        return jsonify(
            {
                "status": "error",
                "message": "COVID-19 ingestion failed",
            }
        ), 500


@app.post("/events/pubsub")
def pubsub_event():
    """Handle Pub/Sub CloudEvents delivered by Eventarc."""

    try:
        event = request.get_json(silent=True) or {}

        LOGGER.info("Received Eventarc event")

        message = event.get("message") or {}

        encoded_data = message.get("data")

        if not encoded_data:
            return jsonify(
                {
                    "status": "error",
                    "message": "Missing Pub/Sub message data",
                }
            ), 400

        decoded_data = base64.b64decode(encoded_data).decode("utf-8")
        gcs_event = json.loads(decoded_data)

        bucket = (
            gcs_event.get("bucket")
            or gcs_event.get("data", {}).get("bucket")
            or BUCKET_NAME
        )

        source = (
            gcs_event.get("name")
            or gcs_event.get("object")
            or gcs_event.get("data", {}).get("name")
        )

        if not source:
            return jsonify(
                {
                    "status": "error",
                    "message": "Could not determine GCS object name",
                }
            ), 400

        source = unquote(source)

        LOGGER.info(
            "Eventarc requested ingestion: gs://%s/%s",
            bucket,
            source,
        )

        return process_ingestion(bucket=bucket, source=source)

    except Exception:
        LOGGER.exception("COVID-19 Eventarc processing failed")

        return jsonify(
            {
                "status": "error",
                "message": "COVID-19 Eventarc processing failed",
            }
        ), 500


def process_ingestion(bucket: str, source: str):
    """Run the ingestion pipeline for a GCS object."""

    LOGGER.info(
        "Starting ingestion: gs://%s/%s",
        bucket,
        source,
    )

    rows_loaded = run(
        source=source,
        bucket=bucket,
    )

    LOGGER.info(
        "Loaded %d rows from gs://%s/%s",
        rows_loaded,
        bucket,
        source,
    )

    return jsonify(
        {
            "status": "success",
            "bucket": bucket,
            "object": source,
            "rows_loaded": rows_loaded,
        }
    ), 200