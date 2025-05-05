"""
Servicio para procesar plantillas y extraer campos dinámicos.
"""

import re
import yaml
import logging
from typing import List, Dict, Any

logger = logging.getLogger("template_service")

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
        # Extraer el bloque YAML original de 'template' como texto, preservando el formato y orden
        import re
        template_match = re.search(r"template:\s*([\s\S]+)", yaml_str)
        if template_match:
            # El bloque comienza justo después de 'template:' (incluye indentación)
            yaml_content = template_match.group(1)
            # Quitar posibles espacios en blanco iniciales
            yaml_content = yaml_content.lstrip('\n')
        else:
            yaml_content = ""
        user_fields = metadata.get("user_fields")
        if user_fields and isinstance(user_fields, list):
            fields = user_fields
        else:
            # fallback: solo nombre de campo
            fields = [{"field": f, "label": f, "type": "string", "required": True} for f in extract_fields_from_yaml(yaml_content)]
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
            "yaml_content": yaml_content
        }
        if not result["name"] or not result["description"]:
            raise ValueError("La plantilla debe tener 'name' y 'description' en metadata.")
        return result
    except Exception as e:
        logger.error(f"Error al parsear plantilla YAML -> {e}", exc_info=True)
        raise ValueError(f"Error al parsear plantilla YAML: {e}")

