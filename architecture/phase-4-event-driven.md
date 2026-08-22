# Phase 4 — Pub/Sub / Event-Driven Ingestion

## Objective

Make the Phase 3 Cloud Run ingestion automatic when a new CSV object is finalized in Cloud Storage.

## Architecture

```text
GCS
  ↓ OBJECT_FINALIZE
Pub/Sub
  ↓
Eventarc
  ↓
Cloud Run
  ↓
Python
  ↓
Validation
  ↓
Transformation
  ↓
BigQuery
```

The existing Python ingestion code is reused. Phase 4 adds only the event adapter under `src/covid_pipeline/events/` and the GCP event infrastructure.

## Components added

- `terraform/pubsub.tf`
  - Pub/Sub topic
  - Cloud Storage notification
  - Eventarc API
  - Eventarc trigger service account
  - Eventarc trigger
  - Cloud Run invocation permission
- `src/covid_pipeline/events/pubsub_handler.py`
  - decodes the Pub/Sub message
  - extracts the Cloud Storage bucket/object
  - invokes the existing `covid_pipeline.main.run()` pipeline
- `POST /events/pubsub`
  - Eventarc destination endpoint

## Event flow

When a CSV is uploaded/finalized in the configured bucket, Cloud Storage publishes a JSON notification to `covid-gcs-events`. Eventarc consumes that Pub/Sub message and invokes the authenticated Cloud Run service. The handler extracts the object name and calls the same ingestion pipeline used in Phase 3.

## Deployment

Phase 3 container image remains valid; no new Python runtime dependency is required.

```bash
cd terraform
terraform init
terraform apply \
  -var="project_id=YOUR_PROJECT" \
  -var="location=us-central1" \
  -var="container_image=REGION-docker.pkg.dev/YOUR_PROJECT/covid-data/covid-pipeline:phase-4"
```

If the Cloud Run image was already built for Phase 3, rebuild it with the Phase 4 source before applying Terraform.

## Manual test

Upload a CSV to the configured bucket:

```bash
gsutil cp data/sample/covid_sample.csv gs://YOUR_BUCKET/sample/covid_sample.csv
```

Then inspect Cloud Run logs:

```bash
gcloud run services logs read covid-pipeline --region=YOUR_REGION --limit=50
```

## Phase boundaries

- **Phase 3:** authenticated manual HTTP invocation of Cloud Run.
- **Phase 4:** automatic GCS object-finalized events through Pub/Sub/Eventarc.
- **Phase 5:** scheduled quality and reconciliation jobs.
- **Phase 6:** Secret Manager and security hardening.
- **Phase 7:** CI/CD, monitoring and production operations.
