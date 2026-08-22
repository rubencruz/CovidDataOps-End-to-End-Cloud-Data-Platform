import pandas as pd
from covid_pipeline.ingestion.transformer import transform

def test_transform_converts_types_and_empty_values():
    df = pd.DataFrame([{
        "regiao": "Norte", "estado": "TO", "municipio": "Wanderlândia",
        "coduf": "17", "codmun": "172208", "codRegiaoSaude": "17001",
        "nomeRegiaoSaude": "MEDIO NORTE ARAGUAIA", "data": "2025-09-02",
        "semanaEpi": "36", "populacaoTCU2019": "11683",
        "casosAcumulado": "2686", "casosNovos": "0",
        "obitosAcumulado": "24", "obitosNovos": "0",
        "Recuperadosnovos": "", "emAcompanhamentoNovos": "",
        "interior_metropolitana": "0",
    }])
    result = transform(df)
    assert result.loc[0, "coduf"] == 17
    assert result.loc[0, "data"].isoformat() == "2025-09-02"
    assert pd.isna(result.loc[0, "Recuperadosnovos"])
    assert pd.isna(result.loc[0, "emAcompanhamentoNovos"])
    assert result.loc[0, "interior_metropolitana"] == 0
