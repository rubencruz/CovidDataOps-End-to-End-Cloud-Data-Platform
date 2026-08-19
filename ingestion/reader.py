"""Read COVID CSV files from GCS or local disk."""
from io import BytesIO
import pandas as pd
from google.cloud import storage
from .config import CSV_DELIMITER, CSV_ENCODING

def read_local_csv(file_path: str) -> pd.DataFrame:
    return pd.read_csv(file_path, sep=CSV_DELIMITER, encoding=CSV_ENCODING,
                       dtype=str, keep_default_na=False)

def read_gcs_csv(bucket_name: str, object_name: str) -> pd.DataFrame:
    client = storage.Client()
    blob = client.bucket(bucket_name).blob(object_name)
    content = blob.download_as_bytes()
    return pd.read_csv(BytesIO(content), sep=CSV_DELIMITER,
                       encoding=CSV_ENCODING, dtype=str, keep_default_na=False)

def read_csv(source: str, bucket_name: str | None = None) -> pd.DataFrame:
    return read_gcs_csv(bucket_name, source) if bucket_name else read_local_csv(source)
