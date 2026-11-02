import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))
import app as app_module

def test_flujo_usuario_completo(tmp_path, monkeypatch):
    monkeypatch.setattr(app_module, "DATABASE", tmp_path / "flow.db")
    app_module.init_db()
    client = app_module.app.test_client()
    email = "flujo@example.com"
    assert client.post("/api/auth/registro", json={"nombre": "Ana", "apellido": "Test", "email": email, "password": "Secreta123", "contacto_confianza": "112233"}).status_code == 201
    assert client.post("/api/auth/login", json={"email": email, "password": "Secreta123"}).status_code == 200
    assert client.post("/api/diario/pin", json={"pin": "1234"}).status_code == 200
    note = client.post("/api/notas", json={"titulo": "Día", "texto": "Hoy me senti tranquila"})
    assert note.status_code == 201
    note_id = note.get_json()["id"]
    assert client.put(f"/api/notas/{note_id}", json={"titulo": "Día editado", "texto": "Hoy me senti feliz"}).status_code == 200
    assert client.delete(f"/api/notas/{note_id}").status_code == 200
    assert client.post("/api/chat", json={"mensaje": "Me quiero hacer daño"}).get_json()["nivel"] == "critico"
    assert client.delete("/api/chat").status_code == 200

def test_admin_no_expone_contenido_privado(tmp_path, monkeypatch):
    monkeypatch.setattr(app_module, "DATABASE", tmp_path / "admin.db")
    app_module.init_db()
    client = app_module.app.test_client()
    assert client.post("/api/auth/login", json={"email": "admin@mentesegura.local", "password": "Admin123!", "documento": "30123456"}).status_code == 200
    response = client.get("/api/admin")
    assert response.status_code == 200
    assert "chat_mensajes" not in response.get_data(as_text=True)

def test_admin_crud_biblioteca(tmp_path, monkeypatch):
    monkeypatch.setattr(app_module, "DATABASE", tmp_path / "admin-crud.db")
    app_module.init_db()
    client = app_module.app.test_client()
    client.post("/api/auth/login", json={"email": "admin@mentesegura.local", "password": "Admin123!", "documento": "30123456"})
    created = client.post("/api/admin/biblioteca", json={"titulo": "Recurso QA", "url": "https://example.com"})
    assert created.status_code == 201
    item_id = created.get_json()["id"]
    assert client.put(f"/api/admin/biblioteca/{item_id}", json={"titulo": "Recurso editado", "url": "https://example.com"}).status_code == 200
    assert client.delete(f"/api/admin/biblioteca/{item_id}").status_code == 200
