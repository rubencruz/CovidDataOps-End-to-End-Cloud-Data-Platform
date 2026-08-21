# Phase 3 — Cloud Run

## Goal

Move the Phase 2 Python application from local execution to a managed Cloud Run container without changing the core ingestion logic.

## Architecture

```text
GCS
 ↓
Cloud Run
 ↓
Python ingestion application
 ↓
BigQuery
```

## Execution model

Cloud Run exposes:

- `GET /health` — liveness endpoint.
- `POST /ingest` — receives `{ "bucket": "...", "object": "..." }` and runs the same read → validate → transform → load pipeline used locally.

The service is authenticated by default. Phase 4 will replace manual HTTP invocation with an event-driven GCS → Eventarc → Cloud Run flow.

## Security

The Cloud Run runtime service account receives:

- `roles/storage.objectViewer` on the ingestion bucket.
- `roles/bigquery.jobUser` on the project.
- `roles/bigquery.dataEditor` on the target dataset.

No service-account keys are embedded in the image.
