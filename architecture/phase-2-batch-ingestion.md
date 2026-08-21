# Phase 2 — Batch Ingestion

```text
GCS -> Python -> Validation -> Transformation -> BigQuery
```

The ingestion package reads the Brazilian COVID CSV, validates the expected schema/business rules, transforms data types and loads the result into BigQuery.
