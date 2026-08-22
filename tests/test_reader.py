import pandas as pd
from covid_pipeline.ingestion.reader import read_local_csv

def test_read_local_csv(tmp_path):
    csv_file = tmp_path / "covid.csv"
    csv_file.write_text(
        "regiao;estado;municipio;coduf;codmun;codRegiaoSaude;nomeRegiaoSaude;"
        "data;semanaEpi;populacaoTCU2019;casosAcumulado;casosNovos;"
        "obitosAcumulado;obitosNovos;Recuperadosnovos;emAcompanhamentoNovos;"
        "interior_metropolitana\n"
        "Norte;TO;Wanderlândia;17;172208;17001;MEDIO NORTE ARAGUAIA;"
        "2025-09-02;36;11683;2686;0;24;0;;;0\n",
        encoding="utf-8",
    )
    df = read_local_csv(str(csv_file))
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert df.loc[0, "estado"] == "TO"
