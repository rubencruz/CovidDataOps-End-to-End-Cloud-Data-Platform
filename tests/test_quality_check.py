from types import SimpleNamespace

from covid_pipeline.jobs import quality_check


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

    assert result["status"] == "passed"
    assert result["total_rows"] == 10
