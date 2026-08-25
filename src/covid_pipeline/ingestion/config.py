"""Configuration for the Phase 2 batch ingestion pipeline."""
import os

#PROJECT_ID = os.getenv("GCP_PROJECT_ID", "gcp-project-506020")
PROJECT_ID = os.environ["GCP_PROJECT_ID"]
#BUCKET_NAME = os.getenv("COVID_BUCKET_NAME", "backet_covid_gcp")
BUCKET_NAME = os.environ["COVID_BUCKET_NAME"]
BQ_DATASET = os.getenv("BQ_DATASET", "covid_raw")
BQ_TABLE = os.getenv("BQ_TABLE", "covid_brazil")
CSV_DELIMITER = ";"
CSV_ENCODING = os.getenv("CSV_ENCODING", "utf-8")

EXPECTED_COLUMNS = [
    "regiao", "estado", "municipio", "coduf", "codmun",
    "codRegiaoSaude", "nomeRegiaoSaude", "data", "semanaEpi",
    "populacaoTCU2019", "casosAcumulado", "casosNovos",
    "obitosAcumulado", "obitosNovos", "Recuperadosnovos",
    "emAcompanhamentoNovos", "interior_metropolitana",
]

INTEGER_COLUMNS = [
    "coduf", "codmun", "codRegiaoSaude", "semanaEpi",
    "populacaoTCU2019", "casosAcumulado", "casosNovos",
    "obitosAcumulado", "obitosNovos", "Recuperadosnovos",
    "emAcompanhamentoNovos", "interior_metropolitana",
]
DATE_COLUMN = "data"
