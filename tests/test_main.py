import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_ok():
    """
    Prueba básica: la raíz responde 200 y contiene el título.
    """
    resp = client.get("/")
    assert resp.status_code == 200
    assert "EasyVPS" in resp.text

def test_root_edge_case():
    """
    Edge case: petición con headers extraños.
    """
    resp = client.get("/", headers={"X-Weird-Header": "test"})
    assert resp.status_code == 200

def test_root_failure():
    """
    Failure: método no permitido.
    """
    resp = client.post("/")
    assert resp.status_code == 405
