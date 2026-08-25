# Phase 6 — Change Inventory

This release is based on the completed Phase 5 project. The existing GCS → Pub/Sub →
Eventarc → Cloud Run ingestion path and Cloud Scheduler jobs remain unchanged.

## New objects

| Object | Change |
|---|---|
| `terraform/security.tf` | **NEW** — enables Secret Manager, creates the runtime secret container and grants the processor secret-access permission. |
| `google_project_service.secret_manager_api` | **NEW** — Secret Manager API activation. |
| `google_secret_manager_secret.pipeline_runtime` | **NEW** — `covid-pipeline-runtime` secret container; no secret value is stored in Terraform. |
| `google_secret_manager_secret_iam_member.processor_accessor` | **NEW** — grants `roles/secretmanager.secretAccessor` only to the Cloud Run processor identity. |
| `output.runtime_secret_name` | **NEW** — exposes the provisioned secret name. |
| `output.security_ingress` | **NEW** — exposes the Cloud Run ingress mode. |

## Modified objects

| Object | Change |
|---|---|
| `terraform/iam.tf` | **UPDATED** — BigQuery `dataEditor` scope is reduced from the entire raw dataset to the `covid_brazil` table. |
| `terraform/storage.tf` | **UPDATED** — enables Public Access Prevention and object versioning. |
| `terraform/cloud_run.tf` | **UPDATED** — explicitly uses Cloud Run Gen2 execution environment while retaining authenticated ingress. |
| `terraform/variables.tf` | **UPDATED** — formalizes `enable_secrets` and adds `secret_name`; Secret Manager is enabled by default. |
| `terraform/outputs.tf` | **UPDATED** — adds Phase 6 security outputs. |
| `architecture/phase-6-security.md` | **UPDATED** — full Phase 6 security architecture, deployment and verification guide. |
| `README.md` | **UPDATED** — Phase 6 documentation and deployment instructions. |
| `scripts/deploy.sh` | **UPDATED** — builds/deploys the Phase 6 container image and uses the current Terraform variable names. |

## Intentionally preserved

- `terraform/pubsub.tf` and the Eventarc architecture
- `terraform/scheduler.tf` and both Scheduler jobs
- Cloud Run service and existing endpoints
- Eventarc and Scheduler dedicated service accounts
- ingestion, transformation and validation code
- Phase 5 data-quality and reconciliation jobs
- existing tests

## Security design decision: no secret value in Terraform

Phase 6 creates the Secret Manager **container** but does not create a secret version.
This avoids placing credentials in Terraform configuration or state. A real secret can
be added later with `gcloud secrets versions add` using the documented command.
