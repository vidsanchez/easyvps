import pytest
from app.services import validation_service

fields = [
    {
        "field": "subdominio",
        "label": "Subdominio",
        "type": "string",
        "required": True,
        "default": "",
        "description": "Config para subdominio",
        "validation": {
            "pattern": "^[a-z0-9-]+$",
            "min_length": None,
            "max_length": None
        }
    },
    {
        "field": "password",
        "label": "Password",
        "type": "password",
        "required": True,
        "default": "",
        "description": "Config para password",
        "validation": {
            "pattern": None,
            "min_length": 8,
            "max_length": 100
        }
    }
]

def test_valid_ok():
    values = {"subdominio": "mi-subdominio", "password": "12345678"}
    validated, errors = validation_service.validate_user_fields(fields, values)
    assert errors is None
    assert validated.subdominio == "mi-subdominio"
    assert validated.password == "12345678"

def test_missing_required():
    values = {"subdominio": "algo"}
    validated, errors = validation_service.validate_user_fields(fields, values)
    assert validated is None
    assert any("password" in e for e in errors)

def test_pattern_fail():
    values = {"subdominio": "MAYUSCULAS", "password": "12345678"}
    validated, errors = validation_service.validate_user_fields(fields, values)
    assert validated is None
    assert any("subdominio" in e for e in errors)

def test_min_length_fail():
    values = {"subdominio": "ok", "password": "123"}
    validated, errors = validation_service.validate_user_fields(fields, values)
    assert validated is None
    assert any("password" in e for e in errors)
