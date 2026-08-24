resource "google_cloud_run_v2_service" "covid_pipeline" {
  name     = var.cloud_run_service_name
  location = var.location
  ingress  = "INGRESS_TRAFFIC_ALL"

  deletion_protection = true

  template {
    service_account       = google_service_account.covid_processor.email
    execution_environment = "EXECUTION_ENVIRONMENT_GEN2"

    scaling {
      min_instance_count = var.min_instances
      max_instance_count = var.max_instances
    }

    containers {
      image = var.container_image

      resources {
        limits = {
          cpu    = var.cpu
          memory = var.memory
        }
      }

      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
      }
      env {
        name  = "COVID_BUCKET_NAME"
        value = google_storage_bucket.covid.name
      }
      env {
        name  = "BQ_DATASET"
        value = var.dataset_id
      }
      env {
        name  = "BQ_TABLE"
        value = var.table_id
      }
    }
  }

  depends_on = [google_project_service.cloud_run_api]
}

resource "google_cloud_run_v2_service_iam_member" "invoker" {
  count    = var.allow_unauthenticated ? 1 : 0
  name     = google_cloud_run_v2_service.covid_pipeline.name
  location = google_cloud_run_v2_service.covid_pipeline.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}
