"""Transform source data into BigQuery-compatible types."""
import pandas as pd
from .config import DATE_COLUMN, INTEGER_COLUMNS

def transform(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    for column in result.columns:
        result[column] = result[column].replace(r"^\s*$", pd.NA, regex=True)

    for column in INTEGER_COLUMNS:
        result[column] = pd.to_numeric(result[column], errors="coerce").astype("Int64")

    result[DATE_COLUMN] = pd.to_datetime(result[DATE_COLUMN], errors="coerce").dt.date

    for column in ["regiao", "estado", "municipio", "nomeRegiaoSaude"]:
        result[column] = result[column].astype("string")

    return result
