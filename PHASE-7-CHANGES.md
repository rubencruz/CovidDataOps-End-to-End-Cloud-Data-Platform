# Phase 7 — Change Inventory

## New

- `terraform/monitoring.tf`: Monitoring and Logging APIs, log-based metrics, alert policies, notification channel and production dashboard.
- `src/covid_pipeline/observability.py`: structured JSON logging and request correlation.
- `.github/workflows/ci.yml`: Python tests and Terraform validation.
- `.github/workflows/deploy.yml`: manual production deployment using GitHub OIDC/WIF.
- `runbooks/production.md`: operational response and recovery procedures.

## Modified

- `terraform/cloud_run.tf`: exposes release version and log level to Cloud Run.
- `terraform/variables.tf`: adds alert thresholds, notification email and application version.
- `terraform/iam.tf`: removes the broad raw-dataset `dataEditor` grant; table-level access remains.
- `src/covid_pipeline/app.py`: request IDs and structured request completion logs.
- `src/covid_pipeline/main.py`: structured ingestion telemetry.
- `scripts/deploy.sh`: builds/deploys the Phase 7 image and passes the release version.
- `README.md`: Phase 7 deployment, monitoring and operations documentation.

## Preserved

- GCS -> Pub/Sub -> Eventarc -> Cloud Run ingestion path.
- Cloud Scheduler quality and reconciliation jobs.
- Phase 6 Secret Manager design without secret values in Terraform.
