import pytest
from app.services import compose_generator

def test_render_compose_template():
    yaml = "services:\n  app:\n    command: run --user=[[username]] --pass=[[password]]"
    values = {"username": "foo", "password": "bar"}
    out = compose_generator.render_compose_template(yaml, values)
    assert "foo" in out and "bar" in out

def test_render_compose_template_missing():
    yaml = "services:\n  app:\n    command: run --user=[[username]] --pass=[[password]]"
    values = {"username": "foo"}
    out = compose_generator.render_compose_template(yaml, values)
    assert "[[password]]" in out

def test_render_compose_template_edge():
    yaml = "services:\n  app:\n    command: echo [[user-name]]"
    values = {"user-name": "baz"}
    out = compose_generator.render_compose_template(yaml, values)
    assert "baz" in out
