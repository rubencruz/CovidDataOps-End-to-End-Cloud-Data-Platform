# Phase 5 — Change Inventory

This release is based on the completed Phase 4 project and preserves the existing ingestion and event-driven architecture.

## Updated objects

| Object | Change |
|---|---|
| `terraform/scheduler.tf` | **NEW** — Cloud Scheduler API and two scheduled jobs: quality check and reconciliation. |
| `terraform/iam.tf` | **UPDATED** — adds the dedicated `covid-scheduler` service account and Cloud Run `roles/run.invoker` permission. |
| `terraform/variables.tf` | **UPDATED** — enables Scheduler by default and adds schedule/time-zone variables. |
| `terraform/outputs.tf` | **UPDATED** — exposes Cloud Run URL, Scheduler service account and configured schedules. |
| `src/covid_pipeline/jobs/__init__.py` | **NEW** — scheduled-job package. |
| `src/covid_pipeline/jobs/quality_check.py` | **NEW** — BigQuery data-quality checks. |
| `src/covid_pipeline/jobs/reconciliation.py` | **NEW** — lineage/reconciliation and duplicate-key checks. |
| `src/covid_pipeline/app.py` | **UPDATED** — adds `/jobs/quality-check` and `/jobs/reconciliation`; existing endpoints remain intact. |
| `tests/test_quality_check.py` | **NEW** — unit test for the quality-check job. |
| `tests/test_reconciliation.py` | **NEW** — unit test for reconciliation. |
| `tests/test_scheduler_routes.py` | **NEW** — tests the two Cloud Run job endpoints. |
| `architecture/phase-5-scheduler.md` | **UPDATED** — Phase 5 architecture, deployment and verification. |
| `README.md` | **UPDATED** — Phase 5 documentation and commands. |
| `terraform/pubsub.tf` | **COMPATIBILITY CORRECTION** — changes the Eventarc filter block from `event_filters` to the provider-supported `matching_criteria`. No Phase 4 architecture or behavior is changed. |

## Objects with no functional modification

The following Phase 1–4 components are intentionally preserved:

- `terraform/provider.tf`
- `terraform/storage.tf`
- `terraform/bigquery.tf`
- `terraform/bigquery_tables.tf`
- `terraform/cloud_run.tf`
- `terraform/pubsub.tf` except for the compatibility correction noted above
- existing IAM permissions for the COVID processor and Eventarc
- `src/covid_pipeline/ingestion/*`
- `src/covid_pipeline/events/*`
- `src/covid_pipeline/main.py`
- `src/covid_pipeline/config/*`
- `schemas/covid_brazil_schema.json`
- existing Phase 2–4 unit tests
- `Dockerfile`
- `requirements.txt`
- deployment/setup/destroy scripts
- Phase 1–4 architecture documents, except README cross-phase documentation

## Phase 5 does not add

- Secret Manager
- new Pub/Sub topics
- new Eventarc triggers
- new Cloud Run services
- CI/CD workflows
- monitoring dashboards or alert policies

Those remain reserved for Phases 6 and 7 according to the project roadmap.
