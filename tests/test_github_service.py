import pytest
from app.services import github_service
import os

def test_list_yaml_files(monkeypatch):
    """
    Prueba que list_yaml_files devuelve solo archivos YAML.
    """
    def fake_get(*args, **kwargs):
        class Resp:
            def raise_for_status(self): pass
            def json(self):
                return [
                    {"name": "foo.yaml"},
                    {"name": "bar.yml"},
                    {"name": "readme.md"}
                ]
        return Resp()
    monkeypatch.setattr(github_service.requests, "get", fake_get)
    files = github_service.list_yaml_files("repo", "path")
    assert files == ["foo.yaml", "bar.yml"]

def test_get_file_content_cache(monkeypatch):
    """
    Prueba que get_file_content usa cache.
    """
    github_service.CACHE.clear()
    key = "repo:path"
    github_service.CACHE[key] = "cached!"
    out = github_service.get_file_content("repo", "path", use_cache=True)
    assert out == "cached!"

def test_get_file_content_no_cache(monkeypatch):
    """
    Prueba que get_file_content descarga y decodifica base64.
    """
    github_service.CACHE.clear()
    import base64
    def fake_get(*args, **kwargs):
        class Resp:
            def raise_for_status(self): pass
            def json(self):
                return {"content": base64.b64encode(b"hello").decode()}
        return Resp()
    monkeypatch.setattr(github_service.requests, "get", fake_get)
    out = github_service.get_file_content("repo", "path", use_cache=False)
    assert out == "hello"
