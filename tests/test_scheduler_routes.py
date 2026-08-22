from covid_pipeline import app


def test_quality_check_route(monkeypatch):
    monkeypatch.setattr(app, "run_quality_check", lambda: {"status": "passed", "total_rows": 10})
    response = app.app.test_client().post("/jobs/quality-check")
    assert response.status_code == 200
    assert response.get_json()["status"] == "passed"


def test_reconciliation_route(monkeypatch):
    monkeypatch.setattr(app, "run_reconciliation", lambda: {"status": "passed", "total_rows": 10})
    response = app.app.test_client().post("/jobs/reconciliation")
    assert response.status_code == 200
    assert response.get_json()["status"] == "passed"
