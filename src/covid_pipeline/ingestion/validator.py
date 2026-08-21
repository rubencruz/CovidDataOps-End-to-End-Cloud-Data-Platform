"""Schema and business-rule validation."""
import pandas as pd
from .config import EXPECTED_COLUMNS

class ValidationError(ValueError):
    """Raised when input data fails validation."""

def validate_columns(df: pd.DataFrame) -> None:
    if list(df.columns) != EXPECTED_COLUMNS:
        missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
        unexpected = [c for c in df.columns if c not in EXPECTED_COLUMNS]
        raise ValidationError(
            f"Invalid schema. Missing={missing}; Unexpected={unexpected}; "
            f"Expected={EXPECTED_COLUMNS}; Received={list(df.columns)}"
        )

def validate_required_values(df: pd.DataFrame) -> None:
    #for column in ["regiao", "estado", "municipio", "data"]:
    for column in ["regiao", "data"]:
        if df[column].isna().any() or (df[column].astype(str).str.strip() == "").any():
            raise ValidationError(f"Required column '{column}' contains empty values.")

def validate_numeric_columns(df: pd.DataFrame) -> None:
    #columns = ["coduf", "codmun", "codRegiaoSaude", "semanaEpi", "populacaoTCU2019","casosAcumulado", "casosNovos", "obitosAcumulado", "obitosNovos","Recuperadosnovos", "emAcompanhamentoNovos", "interior_metropolitana",]
    columns = ["coduf", "codmun", "codRegiaoSaude", "semanaEpi", "populacaoTCU2019","casosAcumulado", "obitosAcumulado", "obitosNovos","Recuperadosnovos", "emAcompanhamentoNovos", "interior_metropolitana",]
    for column in columns:
        values = pd.to_numeric(df[column], errors="coerce")
        invalid = df[column].astype(str).str.strip().ne("") & values.isna()
        if invalid.any():
            raise ValidationError(f"Column '{column}' contains non-numeric values.")

def validate_business_rules(df: pd.DataFrame) -> None:
    #for column in ["populacaoTCU2019", "casosAcumulado", "casosNovos","obitosAcumulado", "obitosNovos", "Recuperadosnovos","emAcompanhamentoNovos",    ]:
    for column in ["populacaoTCU2019", "casosAcumulado","obitosAcumulado", "Recuperadosnovos","emAcompanhamentoNovos",    ]:
        values = pd.to_numeric(df[column], errors="coerce")
        if (values.dropna() < 0).any():
            raise ValidationError(f"Column '{column}' contains negative values.")

    population = pd.to_numeric(df["populacaoTCU2019"], errors="coerce")
    if (population.dropna() <= 0).any():
        raise ValidationError("Column 'populacaoTCU2019' must be greater than zero.")

    #if (~df["estado"].astype(str).str.strip().str.len().eq(2)).any():
    #    raise ValidationError("Column 'estado' must contain two-character UFs.")

    if pd.to_datetime(df["data"], errors="coerce").isna().any():
        raise ValidationError("Column 'data' contains invalid dates.")

def validate(df: pd.DataFrame) -> None:
    validate_columns(df)
    validate_required_values(df)
    validate_numeric_columns(df)
    validate_business_rules(df)
