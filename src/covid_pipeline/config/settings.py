"""Environment-backed settings for the pipeline."""
from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    project_id: str = os.getenv("GCP_PROJECT_ID", "gcp-project-506020")
    bucket_name: str = os.getenv("COVID_BUCKET_NAME", "backet_covid_gcp")
    bq_dataset: str = os.getenv("BQ_DATASET", "covid_raw")
    bq_table: str = os.getenv("BQ_TABLE", "covid_brazil")
    csv_encoding: str = os.getenv("CSV_ENCODING", "utf-8")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()
