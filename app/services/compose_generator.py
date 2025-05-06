"""
Servicio para generar el archivo docker-compose.yml final.
"""

import re
import logging
import yaml
from typing import Dict, Any

logger = logging.getLogger("compose_generator")

FIELD_PATTERN = re.compile(r"\[\[([a-zA-Z0-9_\-]+)\]\]")

def replace_placeholders(obj: Any, values: Dict[str, Any]) -> Any:
    """
    Reemplaza recursivamente los placeholders [[campo]] en todos los valores string del objeto.

    Args:
        obj (Any): Objeto dict/list/string a procesar.
        values (Dict[str, Any]): Diccionario campo: valor.

    Returns:
        Any: Objeto con los placeholders reemplazados.
    """
    if isinstance(obj, dict):
        return {k: replace_placeholders(v, values) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [replace_placeholders(item, values) for item in obj]
    elif isinstance(obj, str):
        def replacer(match):
            key = match.group(1)
            if key not in values:
                logger.warning(f"Falta valor para '{key}' en compose template.")
                return match.group(0)
            return str(values[key])
        return FIELD_PATTERN.sub(replacer, obj)
    else:
        return obj

def render_compose_template(template_dict: dict, values: Dict[str, Any]) -> str:
    """
    Reemplaza los placeholders [[campo]] en el objeto dict y serializa a YAML correctamente indentado.

    IMPORTANTE: Este método debe recibir el subdiccionario correspondiente al bloque de compose (por ejemplo, el valor de data['template']),
    y NO el diccionario completo de la plantilla YAML. Si pasas el diccionario completo (que contiene la clave 'template'),
    la indentación del YAML generado será incorrecta.

    Args:
        template_dict (dict): Subdiccionario Python que representa SOLO el bloque de compose (por ejemplo, data['template']).
        values (Dict[str, Any]): Diccionario campo: valor.

    Returns:
        str: YAML con los valores reemplazados y correctamente indentados.

    Raises:
        ValueError: Si el diccionario recibido contiene la clave 'template', indicando un uso incorrecto.
    """
    # Validación para evitar errores de indentación por estructura incorrecta.
    if 'template' in template_dict:
        raise ValueError(
            "El diccionario pasado a render_compose_template contiene la clave 'template'. "
            "Debes pasar SOLO el subdiccionario correspondiente al bloque de compose, es decir, data['template']. "
            "Si pasas el diccionario completo, el YAML generado tendrá indentación incorrecta."
        )
    # Assert para asegurar que el diccionario es plano y contiene las claves principales
    assert isinstance(template_dict, dict), "template_dict debe ser un dict."
    main_keys = set(template_dict.keys())
    assert 'version' in main_keys and ('services' in main_keys or 'volumes' in main_keys or 'networks' in main_keys), (
        f"template_dict debe contener al menos la clave 'version' y alguna de 'services', 'volumes' o 'networks'. Claves actuales: {main_keys}"
    )
    logger.debug(f"Claves principales en template_dict: {main_keys}")
    rendered = replace_placeholders(template_dict, values)
    # Forzamos el uso de indentación estándar para evitar errores de YAML
    yaml_str = yaml.safe_dump(
        rendered,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        indent=2
    )
    logger.info("Compose renderizado con dict.")
    return yaml_str
