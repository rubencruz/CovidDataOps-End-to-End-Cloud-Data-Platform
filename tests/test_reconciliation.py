from types import SimpleNamespace

from covid_pipeline.jobs import reconciliation


class FakeQuery:
    def __init__(self, row):
        self.row = row

    def result(self):
        return iter([self.row])


class FakeClient:
    def __init__(self, rows):
        self.rows = iter(rows)

    def query(self, query):
        return FakeQuery(next(self.rows))


def test_reconciliation_passes(monkeypatch):
    rows = [
        SimpleNamespace(
            total_rows=10,
            source_files=2,
            max_data=__import__("datetime").date(2025, 9, 2),
            max_ingestion_date=__import__("datetime").date(2025, 9, 2),
            rows_without_source_file=0,
        ),
        SimpleNamespace(duplicate_rows=0),
    ]
    monkeypatch.setattr(reconciliation.bigquery, "Client", lambda project: FakeClient(rows))

    result = reconciliation.run_reconciliation(project="test-project")

    assert result["status"] == "passed"
    assert result["duplicate_rows"] == 0
