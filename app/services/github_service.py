"""
Servicio para interactuar con GitHub y descargar plantillas.
"""

import os
import requests
import logging
from typing import List, Optional, Dict
from dotenv import load_dotenv

# Cargar variables de entorno automáticamente
load_dotenv()

# Valores por defecto propagados del manual_github_fetch.py
def get_default_repo() -> str:
    """
    Devuelve el repo por defecto para plantillas.
    """
    return os.getenv("EASYVPS_REPO", "vidsanchez/easyvps.templates")

def get_default_token() -> Optional[str]:
    """
    Devuelve el token GitHub por defecto (de entorno).
    """
    return os.getenv("GITHUB_TOKEN")

logger = logging.getLogger("github_service")

GITHUB_API_URL = "https://api.github.com"
CACHE: Dict[str, str] = {}

def get_github_headers(token: Optional[str] = None) -> dict:
    """
    Construye los headers para la API de GitHub.

    Args:
        token (Optional[str]): Token de autenticación.

    Returns:
        dict: Headers para la petición.
    """
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    return headers

def list_yaml_files(repo: str, path: str, token: Optional[str] = None) -> List[str]:
    """
    Lista los archivos YAML en un directorio de un repo GitHub.

    Args:
        repo (str): "owner/repo"
        path (str): Ruta dentro del repo.
        token (Optional[str]): Token de autenticación.

    Returns:
        List[str]: Lista de nombres de archivo YAML.
    """
    url = f"{GITHUB_API_URL}/repos/{repo}/contents/{path}"
    resp = requests.get(url, headers=get_github_headers(token))
    resp.raise_for_status()
    files = resp.json()
    return [f["name"] for f in files if f["name"].endswith(('.yml', '.yaml'))]

def get_file_content(repo: str, path: str, token: Optional[str] = None, use_cache: bool = False) -> str:
    """
    Descarga el contenido de un archivo del repo (con cache en memoria).

    Args:
        repo (str): "owner/repo"
        path (str): Ruta del archivo en el repo.
        token (Optional[str]): Token de autenticación.
        use_cache (bool): Si usar cache en memoria.

    Returns:
        str: Contenido del archivo.
    """
    cache_key = f"{repo}:{path}"
    if use_cache and cache_key in CACHE:
        logger.info(f"Cache hit: {cache_key}")
        return CACHE[cache_key]
    url = f"{GITHUB_API_URL}/repos/{repo}/contents/{path}"
    resp = requests.get(url, headers=get_github_headers(token))
    resp.raise_for_status()
    content = resp.json().get("content", "")
    import base64
    decoded = base64.b64decode(content).decode("utf-8")
    CACHE[cache_key] = decoded
    logger.info(f"Cache set: {cache_key}")
    return decoded
