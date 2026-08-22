variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "location" {
  description = "GCP location used by Cloud Storage and BigQuery"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"
}

variable "bucket_name" {
  description = "Existing Cloud Storage bucket used by the COVID data pipeline"
  type        = string
  default     = "backet_covid_gcp"
}
variable "dataset_id" {
  type    = string
  default = "covid_raw"
}
variable "table_id" {
  type    = string
  default = "covid_brazil"
}
variable "container_image" {
  type = string
}
variable "cloud_run_service_name" {
  type    = string
  default = "covid-pipeline"
}
variable "service_account_id" {
  type    = string
  default = "covid-pipeline"
}
variable "memory" {
  type    = string
  default = "1Gi"
}
variable "cpu" {
  type    = string
  default = "1"
}
variable "min_instances" {
  type    = number
  default = 0
}
variable "max_instances" {
  type    = number
  default = 3
}
variable "allow_unauthenticated" {
  type    = bool
  default = false
}
variable "enable_pubsub" {
  type    = bool
  default = false
}
variable "enable_scheduler" {
  type    = bool
  default = false
}
variable "enable_secrets" {
  type    = bool
  default = false
}