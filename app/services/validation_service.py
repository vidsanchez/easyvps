"""
Servicio para validar los campos definidos en user_fields de una plantilla YAML EasyVPS.
Genera modelos Pydantic dinámicos según la definición de campos y reglas.
"""
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, create_model, Field, validator, ValidationError, constr
import re


def build_pydantic_model(fields: List[Dict[str, Any]]):
    """
    Construye un modelo Pydantic dinámico a partir de user_fields.

    Args:
        fields (List[Dict]): Lista de campos de la plantilla.

    Returns:
        BaseModel: Clase Pydantic lista para validar datos.
    """
    # Mapeo rápido de tipos soportados
    type_map = {
        "string": str,
        "password": str,
        "int": int,
        "float": float,
        # Se pueden añadir más tipos según necesidades
    }
    model_fields = {}
    validators = {}
    for field in fields:
        name = field["field"]
        tipo = type_map.get(field.get("type", "string"), str)
        required = field.get("required", False)
        default = ... if required else field.get("default", None)
        desc = field.get("description", "")
        validation = field.get("validation", {}) or {}
        min_length = validation.get("min_length")
        max_length = validation.get("max_length")
        pattern = validation.get("pattern")
        # Robustez: si vienen como string 'null', conviértelo a None
        if min_length in (None, "null"): min_length = None
        if max_length in (None, "null"): max_length = None
        if pattern in (None, "null", ''): pattern = None
        # Para string, usar constr de Pydantic solo si hay restricciones
        if tipo is str and (min_length is not None or max_length is not None or (pattern is not None and pattern != '')):
            constr_kwargs = {"strip_whitespace": True}
            if min_length is not None:
                constr_kwargs["min_length"] = min_length
            if max_length is not None:
                constr_kwargs["max_length"] = max_length
            if pattern is not None and pattern != '':
                constr_kwargs["regex"] = pattern
            model_fields[name] = (constr(**constr_kwargs), Field(default, description=desc))
        else:
            model_fields[name] = (tipo, Field(default, description=desc))
    DynModel = create_model("TemplateUserFields", **model_fields)
    return DynModel


def validate_user_fields(fields: List[Dict[str, Any]], values: Dict[str, Any]) -> Tuple[Optional[BaseModel], Optional[List[str]]]:
    """
    Valida los valores proporcionados según los campos y reglas de la plantilla.

    Args:
        fields (List[Dict]): Definición de campos de la plantilla.
        values (Dict): Valores enviados por el usuario.

    Returns:
        Tuple[Optional[BaseModel], Optional[List[str]]]: Instancia válida o lista de errores.
    """
    Model = build_pydantic_model(fields)
    try:
        validated = Model(**values)
        return validated, None
    except ValidationError as e:
        errors = [f"{err['loc'][0]}: {err['msg']}" for err in e.errors()]
        return None, errors
