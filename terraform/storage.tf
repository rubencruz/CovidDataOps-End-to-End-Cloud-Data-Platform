resource "google_storage_bucket" "covid" {
  name     = var.bucket_name
  location = var.location

  uniform_bucket_level_access = true

  labels = {
    project     = "covid-data-engineering"
    environment = var.environment
    layer       = "raw"
  }
}