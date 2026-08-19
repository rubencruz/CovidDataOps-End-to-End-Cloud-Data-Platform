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