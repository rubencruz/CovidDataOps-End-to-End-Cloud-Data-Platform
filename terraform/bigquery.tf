resource "google_bigquery_dataset" "covid_raw" {
  dataset_id = var.dataset_id
  location   = var.location

  description = "Raw COVID-19 data received from the source system"

  labels = {
    project     = "covid-data-engineering"
    environment = var.environment
    layer       = "raw"
  }
}

resource "google_bigquery_dataset" "covid_curated" {
  dataset_id = "covid_curated"
  location   = var.location

  description = "Validated and standardized COVID-19 data"

  labels = {
    project     = "covid-data-engineering"
    environment = var.environment
    layer       = "curated"
  }
}

resource "google_bigquery_dataset" "covid_analytics" {
  dataset_id = "covid_analytics"
  location   = var.location

  description = "Analytical COVID-19 datasets"

  labels = {
    project     = "covid-data-engineering"
    environment = var.environment
    layer       = "analytics"
  }
}