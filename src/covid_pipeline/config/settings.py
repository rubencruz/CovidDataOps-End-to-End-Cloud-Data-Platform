"""Environment-backed settings for the pipeline."""
from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    #project_id: str = os.getenv("GCP_PROJECT_ID", "")
    project_id: str = os.environ["GCP_PROJECT_ID"]
    #bucket_name: str = os.getenv("COVID_BUCKET_NAME", "")
    bucket_name: str = os.environ["COVID_BUCKET_NAME"]
    bq_dataset: str = os.getenv("BQ_DATASET", "covid_raw")
    bq_table: str = os.getenv("BQ_TABLE", "covid_brazil")
    csv_encoding: str = os.getenv("CSV_ENCODING", "utf-8")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()
