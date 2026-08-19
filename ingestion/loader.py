"""Load transformed COVID data into BigQuery."""
from datetime import datetime, timezone
import pandas as pd
from google.cloud import bigquery
from .config import BQ_DATASET, BQ_TABLE, PROJECT_ID

def add_ingestion_metadata(df: pd.DataFrame, source_bucket: str,
                           source_file: str) -> pd.DataFrame:
    result = df.copy()
    result["ingestion_timestamp"] = datetime.now(timezone.utc)
    result["source_bucket"] = source_bucket
    result["source_file"] = source_file
    return result

def load_to_bigquery(df: pd.DataFrame, project_id: str | None = None,
                     dataset_id: str = BQ_DATASET, table_id: str = BQ_TABLE,
                     write_disposition: str = "WRITE_APPEND") -> None:
    client = bigquery.Client(project=project_id or PROJECT_ID)
    table_ref = f"{client.project}.{dataset_id}.{table_id}"
    job_config = bigquery.LoadJobConfig(
        write_disposition=write_disposition,
        create_disposition=bigquery.CreateDisposition.CREATE_IF_NEEDED,
        autodetect=False,
    )
    job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
    job.result()
