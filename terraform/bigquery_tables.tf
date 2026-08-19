# BigQuery resources for Phase 2.
#
# The table schema is kept in ../schemas/covid_brazil_schema.json so that the
# Terraform definition and the Python loader use the same contract.
#
# Usage:
#   terraform init
#   terraform plan -var="project_id=YOUR_GCP_PROJECT"
#   terraform apply -var="project_id=YOUR_GCP_PROJECT"
#
# The dataset is created here as well so Phase 2 is self-contained. If the
# dataset already exists, import it before apply:
#   terraform import google_bigquery_dataset.covid_raw PROJECT_ID:DATASET_ID


variable "dataset_id" {
  description = "BigQuery dataset ID."
  type        = string
  default     = "covid_raw"
}

variable "table_id" {
  description = "BigQuery table ID."
  type        = string
  default     = "covid_brazil"
}


resource "google_bigquery_table" "covid_brazil" {
  project             = var.project_id
  dataset_id          = google_bigquery_dataset.covid_raw.dataset_id
  table_id            = var.table_id
  deletion_protection = false

  schema = file("${path.module}/../schemas/covid_brazil_schema.json")

  time_partitioning {
    type  = "DAY"
    field = "data"
  }

  clustering = [
    "estado",
    "municipio",
  ]

  labels = {
    phase = "2"
    data  = "covid"
  }

  depends_on = [
    google_bigquery_dataset.covid_raw,
  ]
}
