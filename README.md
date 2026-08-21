# COVID Data Engineering on GCP

A phased data engineering project that evolves a local Python batch pipeline into a GCP-native ingestion platform.

## Architecture

### Phase 1 — Foundation
GCP foundation: project configuration, Cloud Storage, BigQuery and IAM.

### Phase 2 — Batch ingestion
`GCS -> Python -> Validation -> Transformation -> BigQuery`

The Python application can also run locally against a local CSV for development/testing.

### Phase 3 — Cloud Run
`GCS -> Cloud Run -> Python -> BigQuery`

The **same Python ingestion application** is packaged as a container and executed by Cloud Run. In this phase the Cloud Run service exposes an authenticated HTTP endpoint that receives the GCS bucket/object to process. Automatic GCS event triggering is intentionally left for Phase 4.

## Repository structure

```text
covid-data-engineering-gcp/
├── README.md
├── Dockerfile
├── .dockerignore
├── .gitignore
├── .env.example
├── architecture/
├── data/sample/
├── terraform/
├── src/covid_pipeline/
├── schemas/
├── tests/
├── scripts/
└── .github/workflows/
```

## Phase 3 quick start

### 1. Local development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export GCP_PROJECT_ID="your-project"
python -m covid_pipeline.main --source data/sample/covid_sample.csv
```

On Windows PowerShell:

```powershell
$env:GCP_PROJECT_ID="your-project"
pip install -r requirements.txt
python -m covid_pipeline.main --source data/sample/covid_sample.csv
```

### 2. Build and push the container

```bash
gcloud auth configure-docker REGION-docker.pkg.dev

gcloud builds submit \
  --tag {location}-docker.pkg.dev/YOUR_PROJECT/covid-data/covid-pipeline:phase-3 .
```

### 3. Deploy Cloud Run with Terraform

```bash
cd terraform
terraform init
terraform apply \
  -var="project_id=YOUR_PROJECT" \
  -var="location=us-central1" \
  -var="container_image=REGION-docker.pkg.dev/YOUR_PROJECT/covid-data/covid-pipeline:phase-3"
```

The Cloud Run service account gets only the permissions needed by this phase: read objects from the configured bucket and write/load data into BigQuery.

### 4. Invoke the service

Cloud Run is authenticated by default. Get the service URL from Terraform:

```bash
SERVICE_URL=$(terraform output -raw cloud_run_url)
TOKEN=$(gcloud auth print-identity-token)

curl -X POST "$SERVICE_URL/ingest" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"bucket":"YOUR_BUCKET","object":"sample/covid_sample.csv"}'
```

### 5. Health check

```bash
curl "$SERVICE_URL/health"
```

## Phase boundaries

- **Phase 3:** containerize the existing application and run it on Cloud Run through an authenticated HTTP endpoint.
- **Phase 4:** add Eventarc/GCS event-driven invocation.
- **Phase 5:** add Cloud Scheduler for scheduled execution.
- **Phase 6:** harden secrets, IAM and service identities.
- **Phase 7:** production concerns such as monitoring, retries, observability and operational controls.

## Tests

```bash
pytest -q
```

The integration test requires real GCP credentials and is skipped unless `RUN_GCP_INTEGRATION=1` is set.
