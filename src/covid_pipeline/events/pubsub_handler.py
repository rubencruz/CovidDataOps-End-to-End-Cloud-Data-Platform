"""Handle Pub/Sub events carrying Cloud Storage object notifications."""
from __future__ import annotations

import base64
import json
import logging
from typing import Any

from covid_pipeline.ingestion.config import BUCKET_NAME
from covid_pipeline.main import run

LOGGER = logging.getLogger("coviddataops.events")


def _decode_pubsub_data(event: dict[str, Any]) -> dict[str, Any]:
    """Decode the Pub/Sub message data."""

    message = event.get("message") or {}
    encoded = message.get("data")

    if not encoded:
        raise ValueError("Pub/Sub event is missing message.data")

    try:
        decoded = base64.b64decode(encoded).decode("utf-8")

        LOGGER.info("Decoded Pub/Sub payload: %s", decoded)

        payload = json.loads(decoded)

    except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(
            "Pub/Sub message.data is not valid base64-encoded JSON"
        ) from exc

    if not isinstance(payload, dict):
        raise ValueError(
            "Decoded Cloud Storage notification must be a JSON object"
        )

    return payload

def extract_gcs_object(event: dict[str, Any]) -> tuple[str, str]:
    """Extract GCS bucket and object from a Pub/Sub event."""

    payload = _decode_pubsub_data(event)

    message = event.get("message") or {}
    attributes = message.get("attributes") or {}

    bucket = (
        payload.get("bucket")
        or payload.get("bucketId")
        or attributes.get("bucketId")
        or BUCKET_NAME
    )

    object_name = (
        payload.get("name")
        or payload.get("objectId")
        or attributes.get("objectId")
    )

    LOGGER.info(
        "GCS event extracted: bucket=%s object=%s eventType=%s",
        bucket,
        object_name,
        attributes.get("eventType"),
    )

    if not object_name:
        raise ValueError(
            "Cloud Storage notification is missing object name"
        )

    if not bucket:
        raise ValueError(
            "Cloud Storage notification is missing bucket name"
        )

    return str(bucket), str(object_name)

def handle_pubsub_event(event: dict[str, Any]) -> int:
    """Process a GCS object-finalized notification delivered through Pub/Sub."""
    bucket, object_name = extract_gcs_object(event)

    LOGGER.info("Processing GCS event: gs://%s/%s", bucket, object_name)
    rows_loaded = run(source=object_name, bucket=bucket)
    LOGGER.info("Event-driven ingestion loaded %d rows", rows_loaded)
    return rows_loaded
