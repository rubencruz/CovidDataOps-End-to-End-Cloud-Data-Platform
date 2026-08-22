# Phase 5 — Cloud Scheduler invokes authenticated Cloud Run jobs.
resource "google_project_service" "scheduler_api" {
  count              = var.enable_scheduler ? 1 : 0
  project            = var.project_id
  service            = "cloudscheduler.googleapis.com"
  disable_on_destroy = false
}

resource "google_cloud_scheduler_job" "quality_check" {
  count       = var.enable_scheduler ? 1 : 0
  name        = "covid-quality-check"
  description = "Run scheduled COVID BigQuery data-quality checks"
  schedule    = var.quality_check_schedule
  time_zone   = var.scheduler_time_zone
  region      = var.location

  retry_config {
    retry_count = 3
  }

  http_target {
    uri         = "${google_cloud_run_v2_service.covid_pipeline.uri}/jobs/quality-check"
    http_method = "POST"

    headers = {
      "Content-Type" = "application/json"
    }

    body = base64encode(jsonencode({
      job = "quality-check"
    }))

    oidc_token {
      service_account_email = google_service_account.scheduler[0].email
      audience              = google_cloud_run_v2_service.covid_pipeline.uri
    }
  }

  depends_on = [
    google_project_service.scheduler_api,
    google_cloud_run_v2_service_iam_member.scheduler_invoker,
  ]
}

resource "google_cloud_scheduler_job" "reconciliation" {
  count       = var.enable_scheduler ? 1 : 0
  name        = "covid-reconciliation"
  description = "Run scheduled COVID ingestion reconciliation checks"
  schedule    = var.reconciliation_schedule
  time_zone   = var.scheduler_time_zone
  region      = var.location

  retry_config {
    retry_count = 3
  }

  http_target {
    uri         = "${google_cloud_run_v2_service.covid_pipeline.uri}/jobs/reconciliation"
    http_method = "POST"

    headers = {
      "Content-Type" = "application/json"
    }

    body = base64encode(jsonencode({
      job = "reconciliation"
    }))

    oidc_token {
      service_account_email = google_service_account.scheduler[0].email
      audience              = google_cloud_run_v2_service.covid_pipeline.uri
    }
  }

  depends_on = [
    google_project_service.scheduler_api,
    google_cloud_run_v2_service_iam_member.scheduler_invoker,
  ]
}
