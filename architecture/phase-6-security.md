# Phase 6 — Security Hardening

Phase 6 hardens the Phase 5 platform without changing the existing ingestion,
event-driven or scheduled execution paths.

## Security goals

- Keep Cloud Run authenticated; no public `run.invoker` grant is enabled by default.
- Use dedicated service identities for Cloud Run, Eventarc and Cloud Scheduler.
- Reduce BigQuery write access from the whole dataset to the target COVID table.
- Provision a Secret Manager container without putting secret values in Terraform state.
- Enforce private Cloud Storage access and object versioning.
- Keep the Phase 3/4/5 HTTP routes and Eventarc/Scheduler architecture intact.

## Service identities

```text
GCS service agent
      │ pub/sub publisher
      ▼
Pub/Sub topic
      │
      ▼
Eventarc (covid-eventarc)
      │ run.invoker
      ▼
Cloud Run (covid-data-processor)
      │ storage.objectViewer + bigquery.jobUser + table dataEditor
      ▼
GCS / BigQuery

Cloud Scheduler (covid-scheduler)
      │ run.invoker
      ▼
Cloud Run
```

The Cloud Run service account is the only runtime identity that receives data-access
permissions. Eventarc and Scheduler receive invocation-only permissions.

## Secret Manager

Terraform creates the secret container `covid-pipeline-runtime` and grants the
Cloud Run processor service account `roles/secretmanager.secretAccessor`.

The Phase 6 implementation deliberately does **not** create a `google_secret_manager_secret_version`.
This prevents plaintext credentials from being embedded in Terraform configuration/state.
Populate a secret version separately when an application credential is actually required:

```bash
echo -n 'REPLACE_WITH_SECRET' | gcloud secrets versions add covid-pipeline-runtime \
  --data-file=- \
  --project="$PROJECT_ID"
```

## Cloud Storage hardening

The raw bucket keeps uniform bucket-level access and now also enables:

- Public Access Prevention (`enforced`)
- Object versioning

## BigQuery least privilege

The processor retains `roles/bigquery.jobUser` at project scope because it must submit
load/query jobs, but data write permission is restricted from the entire dataset to the
`covid_brazil` table.

## Deployment

Build the Phase 6 image:

```bash
gcloud builds submit \
  --tag REGION-docker.pkg.dev/YOUR_PROJECT/covid-data/covid-pipeline:phase-6 .
```

Then:

```bash
cd terraform
terraform init
terraform apply \
  -var="project_id=YOUR_PROJECT" \
  -var="location=us-central1" \
  -var="container_image=REGION-docker.pkg.dev/YOUR_PROJECT/covid-data/covid-pipeline:phase-6"
```

## Verification

```bash
terraform plan
terraform output runtime_secret_name
terraform output processor_service_account
terraform output scheduler_service_account
terraform output eventarc_trigger
```

Verify the bucket is not public:

```bash
gcloud storage buckets describe gs://YOUR_BUCKET \
  --format='value(iamConfiguration.publicAccessPrevention)'
```

Verify the runtime secret exists:

```bash
gcloud secrets describe covid-pipeline-runtime --project="$PROJECT_ID"
```

Verify only the intended identities can invoke Cloud Run:

```bash
gcloud run services get-iam-policy covid-pipeline \
  --region=us-central1
```
