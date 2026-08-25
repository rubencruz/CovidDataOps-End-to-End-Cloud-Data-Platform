from types import SimpleNamespace
from covid_pipeline.jobs import quality_check
import logging

LOGGER = logging.getLogger("phase7")

class FakeQuery:
    def __init__(self, row):
        self.row = row

    def result(self):
        return iter([self.row])


class FakeClient:
    def __init__(self, row):
        self.row = row

    def query(self, query):
        return FakeQuery(self.row)


def test_quality_check_passes(monkeypatch):
    row = SimpleNamespace(
        total_rows=10,
        invalid_required_rows=0,
        negative_metric_rows=0,
        missing_ingestion_timestamp_rows=0,
    )
    monkeypatch.setattr(quality_check.bigquery, "Client", lambda project: FakeClient(row))

    result = quality_check.run_quality_check(project="test-project")

    LOGGER.info("Quality check result: %s", result)

    if not passed:
        if result["total_rows"] == 0:
            LOGGER.warning(
                "Nenhum dado encontrado para processar hoje. Finalizando com sucesso."
            )
            result["status"] = "passed"
            return result

        raise RuntimeError(f"Data quality checks failed: {result}")

    return result