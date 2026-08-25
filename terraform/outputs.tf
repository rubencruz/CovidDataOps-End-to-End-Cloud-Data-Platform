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
output "pubsub_topic" {
  description = "Pub/Sub topic receiving Cloud Storage object-finalized notifications"
  value       = google_pubsub_topic.covid_gcs_events.name
}

output "eventarc_trigger" {
  description = "Eventarc trigger forwarding Pub/Sub events to Cloud Run"
  value       = google_eventarc_trigger.covid_gcs_pubsub.name
}


output "cloud_run_url" {
  description = "Cloud Run service URL used by scheduled jobs."
  value       = google_cloud_run_v2_service.covid_pipeline.uri
}

output "scheduler_service_account" {
  description = "Service account used by Cloud Scheduler."
  value       = var.enable_scheduler ? google_service_account.scheduler[0].email : null
}

output "quality_check_schedule" {
  description = "Configured Cloud Scheduler schedule for data quality."
  value       = var.enable_scheduler ? google_cloud_scheduler_job.quality_check[0].schedule : null
}

output "reconciliation_schedule" {
  description = "Configured Cloud Scheduler schedule for reconciliation."
  value       = var.enable_scheduler ? google_cloud_scheduler_job.reconciliation[0].schedule : null
}

output "runtime_secret_name" {
  description = "Secret Manager runtime secret container created by Phase 6."
  value       = var.enable_secrets ? google_secret_manager_secret.pipeline_runtime[0].secret_id : null
}

output "security_ingress" {
  description = "Cloud Run ingress mode; authentication remains required by IAM."
  value       = google_cloud_run_v2_service.covid_pipeline.ingress
}

output "monitoring_dashboard_id" {
  description = "Cloud Monitoring production dashboard ID."
  value       = google_monitoring_dashboard.pipeline.id
}

output "monitoring_alert_policies" {
  description = "Production alert policy IDs."
  value = {
    cloud_run_5xx      = google_monitoring_alert_policy.cloud_run_5xx.id
    application_errors = google_monitoring_alert_policy.pipeline_error_logs.id
    data_quality       = google_monitoring_alert_policy.data_quality.id
  }
}
