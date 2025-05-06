"""
Servicio para procesar plantillas y extraer campos dinámicos.
"""

import re
import yaml
import logging
import textwrap
from typing import List, Dict, Any

logger = logging.getLogger("template_service")

def extract_template_block(yaml_str: str) -> str:
    """
    Extrae el bloque 'template:' como string, preservando indentación y formato.
    Soporta bloques YAML multilínea, comentarios y líneas vacías.
    """
    lines = yaml_str.splitlines()
    # Encuentra la línea 'template:'
    template_idx = None
    for idx, line in enumerate(lines):
        if line.strip() == "template:":
            template_idx = idx
            break
    if template_idx is None or template_idx == len(lines) - 1:
        return ""
    # Calcula la indentación base
    base_indent = len(lines[template_idx]) - len(lines[template_idx].lstrip())
    # Extrae todas las líneas siguientes con más indentación o vacías
    block_lines = []
    for line in lines[template_idx + 1:]:
        # Si la línea está vacía, pertenece al bloque
        if not line.strip():
            block_lines.append("")
            continue
        # Calcula la indentación de la línea
        indent = len(line) - len(line.lstrip())
        if indent > base_indent:
            block_lines.append(line[base_indent+1:] if len(line) > base_indent+1 else "")
        else:
            break
    # Une las líneas preservando saltos de línea originales
    return "\n".join(block_lines).rstrip()


def render_template_block(template_str: str, values: dict) -> str:
    """
    Sustituye los placeholders [[variable]] en el bloque template por los valores dados.
    Args:
        template_str (str): Texto del bloque template.
        values (dict): Diccionario de valores a sustituir.
    Returns:
        str: Texto con los placeholders reemplazados.
    """
    for k, v in values.items():
        template_str = template_str.replace(f"[[{k}]]", str(v))
    return template_str

FIELD_PATTERN = re.compile(r"\[\[([a-zA-Z0-9_\-]+)\]\]")

def extract_fields_from_yaml(yaml_content: str) -> List[str]:
    """
    Extrae campos únicos con formato [[variable]] de un string YAML.

    Args:
        yaml_content (str): YAML como string.

    Returns:
        List[str]: Lista de nombres de campo únicos.
    """
    fields = FIELD_PATTERN.findall(yaml_content)
    unique = list(sorted(set(fields)))
    logger.info(f"Campos extraídos: {unique}")
    return unique

def merge_with_defaults(fields: list[dict], user_values: dict) -> dict:
    """
    Devuelve un nuevo dict con los valores del usuario y, si falta alguno, el default de la plantilla.

    Args:
        fields (list[dict]): Lista de campos de la plantilla (cada uno puede tener 'field' y 'default').
        user_values (dict): Valores recibidos del usuario (pueden faltar claves).

    Returns:
        dict: Diccionario combinado, usando default si el usuario no provee el valor.
    """
    result = dict(user_values) if user_values else {}
    for field in fields:
        key = field.get('field')
        if key not in result or result[key] in (None, ""):
            if 'default' in field:
                result[key] = field['default']
    return result

import logging

def parse_template_file(yaml_str: str) -> Dict[str, Any]:
    """
    Parsea el YAML de plantilla y devuelve metadatos, campos y contenido YAML.

    Args:
        yaml_str (str): Contenido del archivo YAML.

    Returns:
        Dict[str, Any]: Diccionario con 'name', 'description', 'fields', 'yaml_content'.
    """
    logger = logging.getLogger("template_service.parse_template_file")
    try:
        data = yaml.safe_load(yaml_str)
        if not isinstance(data, dict):
            raise ValueError("El YAML de la plantilla no es un diccionario raíz.")
        metadata = data.get("metadata", {})
        # Extraer el bloque 'template' como dict directamente del YAML raíz
        yaml_content_dict = data.get("template", {})
        user_fields = metadata.get("user_fields")
        if user_fields and isinstance(user_fields, list):
            fields = user_fields
        else:
            # fallback: solo nombre de campo, usando extract_fields_from_yaml sobre el string YAML original
            import re
            template_block_match = re.search(r"template:\s*([\s\S]+)", yaml_str)
            if template_block_match:
                yaml_content_str = template_block_match.group(1)
            else:
                yaml_content_str = ""
            fields = [{"field": f, "label": f, "type": "string", "required": True} for f in extract_fields_from_yaml(yaml_content_str)]
        result = {
            "name": metadata.get("name", ""),
            "description": metadata.get("description") or "",
            "icon": metadata.get("icon", None),
            "version": metadata.get("version", ""),
            "category": metadata.get("category", ""),
            "dependencies": metadata.get("dependencies", []),
            "required_networks": metadata.get("required_networks", []),
            "tags": metadata.get("tags", []),
            "fields": fields,
            "yaml_content_dict": yaml_content_dict
        }
        if not result["name"] or not result["description"]:
            raise ValueError("La plantilla debe tener 'name' y 'description' en metadata.")
        return result
    except Exception as e:
        logger.error(f"Error al parsear plantilla YAML -> {e}", exc_info=True)
        raise ValueError(f"Error al parsear plantilla YAML: {e}")

