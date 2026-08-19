variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "location" {
  description = "GCP location used by Cloud Storage and BigQuery"
  type        = string
  default     = "US"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"
}

variable "bucket_name" {
  description = "Existing Cloud Storage bucket used by the COVID data pipeline"
  type        = string
  default     = "backet_covid"
}