import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[1]))
import app as app_module

@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(app_module, "DATABASE", tmp_path / "test.db")
    app_module.init_db()
    app_module.app.config.update(TESTING=True, SECRET_KEY="test-secret")
    return app_module.app.test_client()

def test_api_requiere_sesion(client):
    response = client.get("/api/me")
    assert response.status_code == 401

def test_health_y_docs(client):
    assert client.get("/api/health").get_json()["status"] == "ok"
    assert client.get("/api/openapi.json").status_code == 200
    assert client.get("/api/docs").status_code == 200
