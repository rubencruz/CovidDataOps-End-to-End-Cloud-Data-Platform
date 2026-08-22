# Phase 3 — Cloud Run

## Architecture

```text
GCS
 ↓
Cloud Run
 ↓
Python
 ↓
BigQuery
```

The Phase 2 Python ingestion application is containerized and exposed through authenticated HTTP endpoints. Automatic event-driven invocation is intentionally introduced in Phase 4.
