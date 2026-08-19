"""CLI entry point for the Phase 2 COVID-19 batch ingestion pipeline.

Flow:
    source CSV -> read -> validate -> transform -> add metadata -> BigQuery

Examples:
    python main.py --source ./data/covid.csv
    python main.py --source covid.csv --bucket backet_covid
    python main.py --source path/to/file.csv --bucket backet_covid --write-disposition WRITE_TRUNCATE
"""
from __future__ import annotations

import argparse
import logging
from pathlib import Path

from ingestion.config import BQ_DATASET, BQ_TABLE, BUCKET_NAME, PROJECT_ID
from ingestion.loader import add_ingestion_metadata, load_to_bigquery
from ingestion.reader import read_csv
from ingestion.transformer import transform
from ingestion.validator import validate

LOGGER = logging.getLogger("phase2")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Ingest a Brazilian COVID-19 CSV into BigQuery."
    )
    parser.add_argument(
        "--source",
        required=True,
        help="Local CSV path, or GCS object name when --bucket is provided.",
    )
    parser.add_argument(
        "--bucket",
        default=None,
        help=(
            "GCS bucket containing --source. If omitted, --source is read "
            "from the local filesystem."
        ),
    )
    parser.add_argument("--project", default=PROJECT_ID or None,
                        help="GCP project ID. Defaults to GCP_PROJECT_ID.")
    parser.add_argument("--dataset", default=BQ_DATASET,
                        help=f"BigQuery dataset (default: {BQ_DATASET}).")
    parser.add_argument("--table", default=BQ_TABLE,
                        help=f"BigQuery table (default: {BQ_TABLE}).")
    parser.add_argument(
        "--write-disposition",
        choices=("WRITE_APPEND", "WRITE_TRUNCATE", "WRITE_EMPTY"),
        default="WRITE_APPEND",
        help="BigQuery write disposition (default: WRITE_APPEND).",
    )
    parser.add_argument(
        "--log-level",
        choices=("DEBUG", "INFO", "WARNING", "ERROR"),
        default="INFO",
    )
    return parser


def run(
    source: str,
    bucket: str | None = None,
    project: str | None = None,
    dataset: str = BQ_DATASET,
    table: str = BQ_TABLE,
    write_disposition: str = "WRITE_APPEND",
) -> int:
    """Run the complete ingestion pipeline and return the number of rows loaded."""
    if bucket:
        LOGGER.info("Reading gs://%s/%s", bucket, source)
    else:
        source_path = Path(source)
        if not source_path.is_file():
            raise FileNotFoundError(f"Local CSV file not found: {source_path}")
        LOGGER.info("Reading local file %s", source_path)

    df = read_csv(source, bucket_name=bucket)
    LOGGER.info("Read %d rows and %d columns", len(df), len(df.columns))

    validate(df)
    transformed = transform(df)
    enriched = add_ingestion_metadata(
        transformed,
        source_bucket=bucket or "",
        source_file=source,
    )

    load_to_bigquery(
        enriched,
        project_id=project,
        dataset_id=dataset,
        table_id=table,
        write_disposition=write_disposition,
    )
    LOGGER.info(
        "Loaded %d rows into %s.%s",
        len(enriched),
        dataset,
        table,
    )
    return len(enriched)


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )

    try:
        run(
            source=args.source,
            bucket=args.bucket,
            project=args.project,
            dataset=args.dataset,
            table=args.table,
            write_disposition=args.write_disposition,
        )
    except Exception:
        LOGGER.exception("Phase 2 ingestion failed")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
