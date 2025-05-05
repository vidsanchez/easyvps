"""
Servicio para generar el archivo docker-compose.yml final.
"""

import re
import logging
from typing import Dict

logger = logging.getLogger("compose_generator")

FIELD_PATTERN = re.compile(r"\[\[([a-zA-Z0-9_\-]+)\]\]")

def render_compose_template(yaml_content: str, values: Dict[str, str]) -> str:
    """
    Reemplaza los placeholders [[campo]] en el YAML por los valores dados.

    Args:
        yaml_content (str): YAML con placeholders.
        values (Dict[str, str]): Diccionario campo: valor.

    Returns:
        str: YAML con los valores reemplazados.
    """
    def replacer(match):
        key = match.group(1)
        if key not in values:
            logger.warning(f"Falta valor para '{key}' en compose template.")
            return match.group(0)
        return str(values[key])
    result = FIELD_PATTERN.sub(replacer, yaml_content)
    logger.info("Compose renderizado.")
    return result
