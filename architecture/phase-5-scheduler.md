# Phase 5 — Cloud Scheduler / Data Quality

Phase 5 adds controlled, scheduled operational checks without duplicating the ingestion pipeline.

## Architecture

```text
Cloud Scheduler
       │
       ├── POST /jobs/quality-check
       │             │
       │             ▼
       │          Cloud Run
       │             │
       │             ▼
       │          BigQuery
       │
       └── POST /jobs/reconciliation
                     │
                     ▼
                  Cloud Run
                     │
                     ▼
                  BigQuery
```

The existing Phase 3/4 Cloud Run service remains the execution boundary. Cloud Scheduler uses an authenticated OIDC token from the dedicated `covid-scheduler` service account.

## Scheduled jobs

### Quality check

`src/covid_pipeline/jobs/quality_check.py` validates:

- the table contains data;
- required fields are not null;
- COVID case/death metrics are not negative;
- ingestion lineage timestamp is present.

### Reconciliation

`src/covid_pipeline/jobs/reconciliation.py` checks:

- total rows and source-file coverage;
- latest source data date and ingestion date;
- rows without source-file lineage;
- duplicate business keys (`data`, `coduf`, `codmun`, `regiao`, `municipio`).

A failed check returns HTTP 500 so Cloud Scheduler retry behavior can be applied.

## Default schedules

- Quality check: `0 6 * * *`
- Reconciliation: `30 6 * * *`
- Time zone: `America/Sao_Paulo`

Override them with Terraform variables when needed.

## Deployment

Build a Phase 5 image because the scheduled job endpoints are part of the application:

```bash
gcloud builds submit \
  --tag REGION-docker.pkg.dev/YOUR_PROJECT/covid-data/covid-pipeline:phase-5 .
```

Then apply Terraform:

```bash
cd terraform
terraform init
terraform apply \
  -var="project_id=YOUR_PROJECT" \
  -var="location=us-central1" \
  -var="container_image=REGION-docker.pkg.dev/YOUR_PROJECT/covid-data/covid-pipeline:phase-5"
```

Scheduler resources are enabled by default in Phase 5. Set `-var="enable_scheduler=false"` to suppress their creation.

## Verify

```bash
gcloud scheduler jobs list --location=us-central1

gcloud scheduler jobs run covid-quality-check --location=us-central1
gcloud scheduler jobs run covid-reconciliation --location=us-central1
```
