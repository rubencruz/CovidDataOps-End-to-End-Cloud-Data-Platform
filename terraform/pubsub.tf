# ============================================================
# Phase 4 - Pub/Sub + Cloud Storage + Eventarc
# ============================================================

resource "google_project_service" "pubsub_api" {
  project            = var.project_id
  service            = "pubsub.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "eventarc_api" {
  project            = var.project_id
  service            = "eventarc.googleapis.com"
  disable_on_destroy = false
}

data "google_project" "current" {
  project_id = var.project_id
}

# ------------------------------------------------------------
# Pub/Sub topic
# ------------------------------------------------------------

resource "google_pubsub_topic" "covid_gcs_events" {
  name = "covid-gcs-events"

  depends_on = [
    google_project_service.pubsub_api
  ]
}

# ------------------------------------------------------------
# Allow Cloud Storage to publish to Pub/Sub
# ------------------------------------------------------------

resource "google_pubsub_topic_iam_member" "gcs_publisher" {
  topic  = google_pubsub_topic.covid_gcs_events.name
  role   = "roles/pubsub.publisher"
  member = "serviceAccount:service-${data.google_project.current.number}@gs-project-accounts.iam.gserviceaccount.com"

  depends_on = [
    google_project_service.pubsub_api
  ]
}

# ------------------------------------------------------------
# Cloud Storage -> Pub/Sub
# ------------------------------------------------------------

resource "google_storage_notification" "covid_gcs_object_finalize" {
  bucket         = google_storage_bucket.covid.name
  topic          = google_pubsub_topic.covid_gcs_events.id
  payload_format = "JSON_API_V1"
  event_types    = ["OBJECT_FINALIZE"]

  depends_on = [
    google_pubsub_topic_iam_member.gcs_publisher
  ]
}

# ------------------------------------------------------------
# Eventarc service account
# ------------------------------------------------------------

resource "google_service_account" "eventarc_trigger" {
  account_id   = "covid-eventarc"
  display_name = "COVID Eventarc Trigger"
}

resource "google_project_iam_member" "eventarc_receiver" {
  project = var.project_id
  role    = "roles/eventarc.eventReceiver"
  member  = "serviceAccount:${google_service_account.eventarc_trigger.email}"
}

resource "google_cloud_run_v2_service_iam_member" "eventarc_invoker" {
  name     = google_cloud_run_v2_service.covid_pipeline.name
  location = google_cloud_run_v2_service.covid_pipeline.location
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.eventarc_trigger.email}"
}

# ------------------------------------------------------------
# Pub/Sub -> Eventarc -> Cloud Run
# ------------------------------------------------------------

resource "google_eventarc_trigger" "covid_gcs_pubsub" {
  name     = "covid-gcs-pubsub-to-cloud-run"
  location = var.location

  matching_criteria {
    attribute = "type"
    value     = "google.cloud.pubsub.topic.v1.messagePublished"
  }

  transport {
    pubsub {
      topic = google_pubsub_topic.covid_gcs_events.id
    }
  }

  destination {
    cloud_run_service {
      service = google_cloud_run_v2_service.covid_pipeline.name
      region  = google_cloud_run_v2_service.covid_pipeline.location
      path    = "/events/pubsub"
    }
  }

  service_account = google_service_account.eventarc_trigger.email

  depends_on = [
    google_project_service.pubsub_api,
    google_project_service.eventarc_api,
    google_project_iam_member.eventarc_receiver,
    google_cloud_run_v2_service_iam_member.eventarc_invoker,
    google_pubsub_topic_iam_member.gcs_publisher,
  ]
}