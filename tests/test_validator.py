import pandas as pd
import pytest
from covid_pipeline.ingestion.config import EXPECTED_COLUMNS
from covid_pipeline.ingestion.validator import ValidationError, validate

def valid_dataframe():
    return pd.DataFrame([{
        "regiao": "Norte", "estado": "TO", "municipio": "Wanderlândia",
        "coduf": "17", "codmun": "172208", "codRegiaoSaude": "17001",
        "nomeRegiaoSaude": "MEDIO NORTE ARAGUAIA", "data": "2025-09-02",
        "semanaEpi": "36", "populacaoTCU2019": "11683",
        "casosAcumulado": "2686", "casosNovos": "0",
        "obitosAcumulado": "24", "obitosNovos": "0",
        "Recuperadosnovos": "", "emAcompanhamentoNovos": "",
        "interior_metropolitana": "0",
    }], columns=EXPECTED_COLUMNS)

def test_valid_dataframe():
    validate(valid_dataframe())

def test_missing_required_column():
    with pytest.raises(ValidationError):
        validate(valid_dataframe().drop(columns=["municipio"]))

def test_negative_cumulative_cases_are_rejected():
    df = valid_dataframe()
    df.loc[0, "casosAcumulado"] = "-1"
    with pytest.raises(ValidationError):
        validate(df)
