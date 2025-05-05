import pytest
from app.services import template_service

def test_extract_fields_from_yaml():
    yaml = """
    services:
      app:
        command: run --user=[[username]] --pass=[[password]] --sub=[[subdominio]]
    """
    fields = template_service.extract_fields_from_yaml(yaml)
    assert set(fields) == {"username", "password", "subdominio"}

def test_parse_template_file():
    yaml = """
    metadata:
      name: Test
      description: Desc
    template:
      version: '3.7'
      services:
        app:
          image: test
          command: run --user=[[usuario]]
    """
    result = template_service.parse_template_file(yaml)
    assert result["name"] == "Test"
    assert "usuario" in result["fields"]
    assert "template" in result["yaml_content"]
