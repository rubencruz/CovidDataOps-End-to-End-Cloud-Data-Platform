locals {
  covid_schema = jsondecode(file("${path.module}/../schemas/covid_brazil_schema.json"))
}

resource "google_bigquery_table" "covid_brazil" {
  dataset_id = google_bigquery_dataset.covid_raw.dataset_id
  table_id   = var.table_id

  schema = jsonencode(local.covid_schema)

  time_partitioning {
    type  = "DAY"
    field = "data"
  }

  clustering = ["estado", "municipio"]

  deletion_protection = false
}
