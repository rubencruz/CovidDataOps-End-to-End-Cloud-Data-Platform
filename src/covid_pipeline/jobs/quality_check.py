"""Scheduled BigQuery data-quality checks for the COVID raw dataset."""
from __future__ import annotations

import logging
from typing import Any

from google.cloud import bigquery

from covid_pipeline.ingestion.config import BQ_DATASET, BQ_TABLE, PROJECT_ID

LOGGER = logging.getLogger("coviddataops.jobs.quality")


QUALITY_QUERY = """
SELECT
  COUNT(*) AS total_rows,
  COUNTIF(regiao IS NULL OR coduf IS NULL OR data IS NULL) AS invalid_required_rows,
  COUNTIF(
    -- COALESCE(casosNovos, 0) < 0
    -- OR COALESCE(obitosNovos, 0) < 0
    COALESCE(casosAcumulado, 0) < 0
    OR COALESCE(obitosAcumulado, 0) < 0
  ) AS negative_metric_rows,
  COUNTIF(ingestion_timestamp IS NULL) AS missing_ingestion_timestamp_rows
FROM `{project}.{dataset}.{table}`
"""


def run_quality_check(
    project: str | None = None,
    dataset: str = BQ_DATASET,
    table: str = BQ_TABLE,
) -> dict[str, Any]:
    """Run deterministic quality checks and raise RuntimeError on failure."""
    project = project or PROJECT_ID
    client = bigquery.Client(project=project)
    query = QUALITY_QUERY.format(project=project, dataset=dataset, table=table)
    row = next(iter(client.query(query).result()))

    result = {
        "total_rows": int(row.total_rows),
        "invalid_required_rows": int(row.invalid_required_rows),
        "negative_metric_rows": int(row.negative_metric_rows),
        "missing_ingestion_timestamp_rows": int(row.missing_ingestion_timestamp_rows),
    }

    passed = (
        result["total_rows"] > 0
        and result["invalid_required_rows"] == 0
        and result["negative_metric_rows"] == 0
        and result["missing_ingestion_timestamp_rows"] == 0
    )
    result["status"] = "passed" if passed else "failed"

    LOGGER.info("Quality check result: %s", result)
    if not passed:
        raise RuntimeError(f"Data quality checks failed: {result}")
    return result
