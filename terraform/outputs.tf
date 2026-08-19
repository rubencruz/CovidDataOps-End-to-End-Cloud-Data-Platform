output "project_id" {
  description = "GCP Project ID"
  value       = var.project_id
}

output "bucket_name" {
  description = "COVID raw data bucket"
  value       = google_storage_bucket.covid.name
}

output "bucket_url" {
  description = "Cloud Storage bucket URL"
  value       = "gs://${google_storage_bucket.covid.name}"
}

output "processor_service_account" {
  description = "Service account used by the COVID data processor"
  value       = google_service_account.covid_processor.email
}

output "covid_raw_dataset" {
  description = "Raw BigQuery dataset"
  value       = google_bigquery_dataset.covid_raw.dataset_id
}

output "covid_curated_dataset" {
  description = "Curated BigQuery dataset"
  value       = google_bigquery_dataset.covid_curated.dataset_id
}

output "covid_analytics_dataset" {
  description = "Analytics BigQuery dataset"
  value       = google_bigquery_dataset.covid_analytics.dataset_id
}