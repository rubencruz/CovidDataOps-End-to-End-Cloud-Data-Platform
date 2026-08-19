# Phase 2 — Batch Data Ingestion

Implements the batch ingestion layer for the Brazilian COVID-19 CSV files.

Flow:

Cloud Storage -> Python -> Validation -> Transformation -> BigQuery

Input files use `;` as delimiter. Empty fields are preserved as NULL.

## Environment variables

- `GCP_PROJECT_ID`
- `COVID_BUCKET_NAME` (default: `backet_covid`)
- `BQ_DATASET` (default: `covid_raw`)
- `BQ_TABLE` (default: `covid_brazil`)
- `CSV_ENCODING` (default: `utf-8`)

## Install

```bash
pip install -r requirements.txt
```

## Tests

```bash
pytest -q
```

The BigQuery and GCS clients use Application Default Credentials.


## Entry point

The Phase 2 entry point is `main.py`. It orchestrates the complete flow:

`CSV -> read -> validate -> transform -> metadata -> BigQuery`

### Local CSV

```bash
export GCP_PROJECT_ID="your-gcp-project"
python main.py --source ./data/covid.csv
```

### CSV stored in Google Cloud Storage

```bash
export GCP_PROJECT_ID="your-gcp-project"
export COVID_BUCKET_NAME="backet_covid"

python main.py --source path/to/covid.csv --bucket "$COVID_BUCKET_NAME"
```

When `--bucket` is provided, `--source` is treated as the GCS object name.

### BigQuery Terraform

`terraform/bigquery_tables.tf` creates the `covid_raw` dataset and the
`covid_brazil` table using `schemas/covid_brazil_schema.json`.

```bash
cd terraform
terraform init
terraform plan -var="project_id=your-gcp-project"
terraform apply -var="project_id=your-gcp-project"
```

If the dataset already exists, import it before applying the configuration:

```bash
terraform import google_bigquery_dataset.covid_raw your-gcp-project:covid_raw
```
