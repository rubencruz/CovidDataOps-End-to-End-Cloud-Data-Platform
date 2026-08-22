resource "google_service_account" "covid_processor" {
  account_id   = "covid-data-processor"
  display_name = "COVID Data Processor"
  description  = "Service account used by the COVID data engineering pipeline"
}

#Agora damos permissão para ela ler objetos do bucket:

resource "google_storage_bucket_iam_member" "processor_storage_reader" {
  bucket = google_storage_bucket.covid.name

  role = "roles/storage.objectViewer"

  member = "serviceAccount:${google_service_account.covid_processor.email}"
}

#E permissão para executar jobs no BigQuery:

resource "google_project_iam_member" "processor_bigquery_job_user" {
  project = var.project_id

  role = "roles/bigquery.jobUser"

  member = "serviceAccount:${google_service_account.covid_processor.email}"
}

resource "google_bigquery_dataset_iam_member" "cloud_run_bigquery_editor" {
  project    = var.project_id
  dataset_id = google_bigquery_dataset.covid_raw.dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${google_service_account.covid_processor.email}"
}

# Ativa a API do Cloud Run automaticamente
resource "google_project_service" "cloud_run_api" {
  project            = var.project_id
  service            = "run.googleapis.com"
  disable_on_destroy = false
}

# Phase 5: Cloud Scheduler invokes the authenticated Cloud Run jobs.
resource "google_service_account" "scheduler" {
  count        = var.enable_scheduler ? 1 : 0
  account_id   = "covid-scheduler"
  display_name = "COVID Cloud Scheduler"
  description  = "Identity used by Cloud Scheduler to invoke scheduled Cloud Run jobs"
}

resource "google_cloud_run_v2_service_iam_member" "scheduler_invoker" {
  count    = var.enable_scheduler ? 1 : 0
  name     = google_cloud_run_v2_service.covid_pipeline.name
  location = google_cloud_run_v2_service.covid_pipeline.location
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.scheduler[0].email}"
}
