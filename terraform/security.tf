# Phase 6 — Security hardening
# Secrets are provisioned as Secret Manager containers. Secret values are
# intentionally NOT stored in Terraform state; populate a version out-of-band.

resource "google_project_service" "secret_manager_api" {
  project            = var.project_id
  service            = "secretmanager.googleapis.com"
  disable_on_destroy = false
}

resource "google_secret_manager_secret" "pipeline_runtime" {
  count     = var.enable_secrets ? 1 : 0
  secret_id = var.secret_name

  replication {
    auto {}
  }

  labels = {
    project     = "covid-data-engineering"
    environment = var.environment
    managed_by  = "terraform"
  }

  depends_on = [google_project_service.secret_manager_api]
}

resource "google_secret_manager_secret_iam_member" "processor_accessor" {
  count     = var.enable_secrets ? 1 : 0
  secret_id = google_secret_manager_secret.pipeline_runtime[0].id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.covid_processor.email}"
}

