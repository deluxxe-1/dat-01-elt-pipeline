"""API-level tests for the FastAPI service."""

from fastapi.testclient import TestClient

from elt_pipeline import main


def test_health_endpoint():
    client = TestClient(main.app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_pipeline_run_endpoint(monkeypatch, db_path):
    monkeypatch.setattr(main.settings, "database_path", db_path)
    client = TestClient(main.app)

    response = client.post("/api/pipeline/run", params={"count": 20, "seed": 1})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["extracted"] == 20
    assert body["raw_rows"] == 20
    assert body["mart_rows"] > 0
