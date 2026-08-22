"""Scheduled reconciliation checks for the ingested COVID raw table."""
from __future__ import annotations

import logging
from typing import Any

from google.cloud import bigquery

from covid_pipeline.ingestion.config import BQ_DATASET, BQ_TABLE, PROJECT_ID

LOGGER = logging.getLogger("coviddataops.jobs.reconciliation")


SUMMARY_QUERY = """
SELECT
  COUNT(*) AS total_rows,
  COUNT(DISTINCT source_file) AS source_files,
  MAX(data) AS max_data,
  MAX(DATE(ingestion_timestamp)) AS max_ingestion_date,
  COUNTIF(source_file IS NULL OR source_file = '') AS rows_without_source_file
FROM `{project}.{dataset}.{table}`
"""

DUPLICATE_QUERY = """
SELECT COALESCE(SUM(cnt - 1), 0) AS duplicate_rows
FROM (
  SELECT
    data,
    coduf,
    codmun,
    regiao,
    municipio,
    COUNT(*) AS cnt
  FROM `{project}.{dataset}.{table}`
  GROUP BY data, coduf, codmun, regiao, municipio
  HAVING COUNT(*) > 1
)
"""


def run_reconciliation(
    project: str | None = None,
    dataset: str = BQ_DATASET,
    table: str = BQ_TABLE,
) -> dict[str, Any]:
    """Reconcile row lineage and business-key uniqueness in BigQuery."""
    project = project or PROJECT_ID
    client = bigquery.Client(project=project)
    summary = next(iter(client.query(
        SUMMARY_QUERY.format(project=project, dataset=dataset, table=table)
    ).result()))
    duplicate = next(iter(client.query(
        DUPLICATE_QUERY.format(project=project, dataset=dataset, table=table)
    ).result()))

    result = {
        "total_rows": int(summary.total_rows),
        "source_files": int(summary.source_files),
        "max_data": summary.max_data.isoformat() if summary.max_data else None,
        "max_ingestion_date": summary.max_ingestion_date.isoformat() if summary.max_ingestion_date else None,
        "rows_without_source_file": int(summary.rows_without_source_file),
        "duplicate_rows": int(duplicate.duplicate_rows),
    }

    passed = (
        result["total_rows"] > 0
        and result["source_files"] > 0
        and result["rows_without_source_file"] == 0
        and result["duplicate_rows"] == 0
    )
    result["status"] = "passed" if passed else "failed"

    LOGGER.info("Reconciliation result: %s", result)
    if not passed:
        raise RuntimeError(f"Reconciliation checks failed: {result}")
    return result
