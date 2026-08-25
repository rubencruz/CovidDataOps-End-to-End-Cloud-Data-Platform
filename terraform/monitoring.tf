# Phase 7 — Production monitoring, alerting and operational telemetry.

resource "google_project_service" "monitoring_api" {
  project            = var.project_id
  service            = "monitoring.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "logging_api" {
  project            = var.project_id
  service            = "logging.googleapis.com"
  disable_on_destroy = false
}

resource "google_logging_metric" "pipeline_errors" {
  name        = "covid_pipeline_errors"
  description = "Application error log entries emitted by the COVID pipeline."
  filter      = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"${var.cloud_run_service_name}\" AND severity>=ERROR"

  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
    unit        = "1"
  }

  depends_on = [google_project_service.logging_api]
}

resource "google_logging_metric" "data_quality_failures" {
  name        = "covid_pipeline_data_quality_failures"
  description = "Failed data-quality and reconciliation job executions."
  filter      = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"${var.cloud_run_service_name}\" AND (textPayload:\"Quality check failed\" OR textPayload:\"Reconciliation failed\")"

  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
    unit        = "1"
  }

  depends_on = [google_project_service.logging_api]
}

resource "google_monitoring_notification_channel" "email" {
  count        = var.notification_email == "" ? 0 : 1
  display_name = "COVID pipeline operations email"
  type         = "email"

  labels = {
    email_address = var.notification_email
  }

  depends_on = [google_project_service.monitoring_api]
}

locals {
  alert_notification_channels = var.notification_email == "" ? [] : [google_monitoring_notification_channel.email[0].name]
}

resource "google_monitoring_alert_policy" "cloud_run_5xx" {
  display_name = "COVID pipeline — Cloud Run 5xx errors"
  combiner     = "OR"
  enabled      = true

  conditions {
    display_name = "Cloud Run 5xx rate"
    condition_threshold {
      filter          = "metric.type=\"run.googleapis.com/request_count\" resource.type=\"cloud_run_revision\" resource.label.service_name=\"${var.cloud_run_service_name}\" metric.label.response_code_class=\"5xx\""
      comparison      = "COMPARISON_GT"
      threshold_value = var.cloud_run_5xx_threshold
      duration        = "300s"

      aggregations {
        alignment_period     = "60s"
        per_series_aligner   = "ALIGN_RATE"
        cross_series_reducer = "REDUCE_SUM"
      }
    }
  }

  notification_channels = local.alert_notification_channels
  documentation {
    content   = "Investigate Cloud Run logs using the request_id field. Check recent deployments, upstream GCS/Pub/Sub events and BigQuery load errors."
    mime_type = "text/markdown"
  }

  depends_on = [google_project_service.monitoring_api]
}

resource "google_monitoring_alert_policy" "pipeline_error_logs" {
  display_name = "COVID pipeline — application errors"
  combiner     = "OR"
  enabled      = true

  conditions {
    display_name = "Application error log rate"
    condition_threshold {
      filter          = "metric.type=\"logging.googleapis.com/user/covid_pipeline_errors\" resource.type=\"cloud_run_revision\""
      comparison      = "COMPARISON_GT"
      threshold_value = var.pipeline_error_threshold
      duration        = "300s"

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }

  notification_channels = local.alert_notification_channels
  documentation {
    content   = "Check Cloud Run structured logs and correlate failures with request_id, event_id and source_object."
    mime_type = "text/markdown"
  }

  depends_on = [google_logging_metric.pipeline_errors, google_project_service.monitoring_api]
}

resource "google_monitoring_alert_policy" "data_quality" {
  display_name = "COVID pipeline — data quality failure"
  combiner     = "OR"
  enabled      = true

  conditions {
    display_name = "Quality or reconciliation failure"
    condition_threshold {
      filter          = "metric.type=\"logging.googleapis.com/user/covid_pipeline_data_quality_failures\" resource.type=\"cloud_run_revision\""
      comparison      = "COMPARISON_GT"
      threshold_value = 0
      duration        = "0s"

      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_SUM"
      }
    }
  }

  notification_channels = local.alert_notification_channels
  documentation {
    content   = "A scheduled data-quality or reconciliation job failed. Review the job response and BigQuery data before rerunning."
    mime_type = "text/markdown"
  }

  depends_on = [google_logging_metric.data_quality_failures, google_project_service.monitoring_api]
}

resource "google_monitoring_dashboard" "pipeline" {
  dashboard_json = jsonencode({
    displayName = "COVID Data Pipeline — Production"
    gridLayout = {
      columns = "2"
      widgets = [
        {
          title = "Cloud Run request rate"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "metric.type=\"run.googleapis.com/request_count\" resource.type=\"cloud_run_revision\" resource.label.service_name=\"${var.cloud_run_service_name}\""
                  aggregation = { alignmentPeriod = "60s", perSeriesAligner = "ALIGN_RATE", crossSeriesReducer = "REDUCE_SUM" }
                }
              }
            }]
          }
        },
        {
          title = "Cloud Run latency"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "metric.type=\"run.googleapis.com/request_latencies\" resource.type=\"cloud_run_revision\" resource.label.service_name=\"${var.cloud_run_service_name}\""
                  aggregation = { alignmentPeriod = "60s", perSeriesAligner = "ALIGN_PERCENTILE_99", crossSeriesReducer = "REDUCE_MAX" }
                }
              }
            }]
          }
        },
        {
          title = "Pipeline application errors"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "metric.type=\"logging.googleapis.com/user/covid_pipeline_errors\" resource.type=\"cloud_run_revision\""
                  aggregation = { alignmentPeriod = "60s", perSeriesAligner = "ALIGN_RATE" }
                }
              }
            }]
          }
        },
        {
          title = "Data quality failures"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "metric.type=\"logging.googleapis.com/user/covid_pipeline_data_quality_failures\" resource.type=\"cloud_run_revision\""
                  aggregation = { alignmentPeriod = "300s", perSeriesAligner = "ALIGN_SUM" }
                }
              }
            }]
          }
        }
      ]
    }
  })

  depends_on = [google_project_service.monitoring_api, google_logging_metric.pipeline_errors, google_logging_metric.data_quality_failures]
}
