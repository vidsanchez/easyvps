import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_templates_list():
    """
    Esperado: devuelve lista no vacía de plantillas (repo privado, token requerido).
    """
    resp = client.get("/templates")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert any("id" in t and "name" in t for t in data)

def test_template_detail_ok():
    """
    Esperado: devuelve campos y metadatos de una plantilla conocida.
    """
    # Usa una plantilla que exista en tu repo (ajusta si es necesario)
    template_id = "baserow.yaml"
    resp = client.get(f"/template/{template_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == template_id
    assert "fields" in data and isinstance(data["fields"], list)

def test_template_detail_not_found():
    """
    Edge: plantilla inexistente debe dar 404.
    """
    resp = client.get("/template/no_existe.yaml")
    assert resp.status_code == 404

def test_generate_compose_ok():
    """
    Esperado: genera compose válido para plantilla conocida.
    """
    template_id = "baserow.yaml"
    values = {"username": "test", "password": "secret", "subdominio": "mysub"}
    resp = client.post("/generate", json={"template_id": template_id, "values": values})
    assert resp.status_code == 200
    data = resp.json()
    assert "compose" in data
    assert "test" in data["compose"] and "secret" in data["compose"]

def test_generate_compose_missing_field():
    """
    Edge: falta campo, el compose debe contener el placeholder.
    """
    template_id = "baserow.yaml"
    values = {"username": "test"}
    resp = client.post("/generate", json={"template_id": template_id, "values": values})
    assert resp.status_code == 200
    data = resp.json()
    assert "[[password]]" in data["compose"]

def test_generate_compose_not_found():
    """
    Failure: plantilla no existe, debe dar 400.
    """
    resp = client.post("/generate", json={"template_id": "no_existe.yaml", "values": {}})
    assert resp.status_code == 400

def test_download_compose_ok():
    """
    Descarga exitosa: el archivo contiene los valores enviados.
    """
    template_id = "baserow.yaml"
    params = {"username": "foo", "password": "bar", "subdominio": "mysub"}
    resp = client.get(f"/download/{template_id}", params=params)
    assert resp.status_code == 200
    assert resp.headers["content-disposition"].startswith("attachment")
    content = resp.content.decode()
    assert "foo" in content and "bar" in content and "mysub" in content

def test_download_compose_missing_field():
    """
    Edge: falta un campo, el compose contiene el placeholder.
    """
    template_id = "baserow.yaml"
    params = {"username": "foo"}
    resp = client.get(f"/download/{template_id}", params=params)
    assert resp.status_code == 200
    content = resp.content.decode()
    assert "[[password]]" in content

def test_download_compose_not_found():
    """
    Error: plantilla inexistente, status 400.
    """
    resp = client.get("/download/no_existe.yaml")
    assert resp.status_code == 400
