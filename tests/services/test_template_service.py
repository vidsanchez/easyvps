import pytest
from app.services.template_service import extract_template_block, render_template_block

def test_extract_template_block_basic():
    yaml = '''metadata:
  name: test
  description: test
  user_fields:
    - field: memory
      label: Memoria
      type: string
      required: true
template:
  services:
    redis:
      image: redis:alpine
      mem_limit: '[[memory]]M'
      environment:
        - PASSWORD=[[password]]
'''
    expected = (
        "services:\n"
        "  redis:\n"
        "    image: redis:alpine\n"
        "    mem_limit: '[[memory]]M'\n"
        "    environment:\n"
        "      - PASSWORD=[[password]]"
    )
    block = extract_template_block(yaml)
    assert block.strip() == expected.strip()

def test_extract_template_block_with_blank_lines():
    yaml = '''template:
  services:
    redis:
      image: redis:alpine
      # comentario
      mem_limit: '[[memory]]M'

      environment:
        - PASSWORD=[[password]]
'''
    block = extract_template_block(yaml)
    print(f"\n---BLOQUE EXTRAÍDO---\n{block}\n---FIN BLOQUE---\n")
    assert 'mem_limit: ' in block
    assert "'[[memory]]M'" in block
    assert '\n\n' in block  # conserva líneas en blanco

def test_render_template_block_replacement():
    template = "services:\n  redis:\n    mem_limit: '[[memory]]M'\n    environment:\n      - PASSWORD=[[password]]"
    values = {'memory': 2048, 'password': 'secreta'}
    rendered = render_template_block(template, values)
    assert "mem_limit: '2048M'" in rendered
    assert "PASSWORD=secreta" in rendered
    assert '[[memory]]' not in rendered
    assert '[[password]]' not in rendered

# Edge case: si falta un valor, no se reemplaza

def test_render_template_block_missing_value():
    template = "mem_limit: '[[memory]]M'\npassword: [[password]]"
    values = {'memory': 512}
    rendered = render_template_block(template, values)
    assert "mem_limit: '512M'" in rendered
    assert '[[password]]' in rendered  # no reemplazado
