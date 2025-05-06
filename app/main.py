from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any
import os

from app.services import github_service, template_service, compose_generator

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    """
    Página principal con la lista de plantillas (placeholder).
    """
    return templates.TemplateResponse("index.html", {"request": request, "templates": []})

@app.get("/template_form.html", response_class=HTMLResponse)
def template_form_html(request: Request):
    """
    Sirve el formulario dinámico para la plantilla seleccionada.
    """
    return templates.TemplateResponse("template_form.html", {"request": request})

from typing import Optional

class TemplateListItem(BaseModel):
    id: str
    name: str
    description: str
    icon: Optional[str] = None

from typing import Any

class TemplateDetail(BaseModel):
    id: str
    name: str
    description: str
    version: str = ""
    category: str = ""
    dependencies: list = []
    required_networks: list = []
    tags: list = []
    fields: List[dict[str, Any]]

class GenerateRequest(BaseModel):
    template_id: str
    values: Dict[str, Any]

import logging

@app.get("/templates")
def list_templates():
    """
    Devuelve la lista de plantillas YAML disponibles en el repo.
    """
    repo = github_service.get_default_repo()
    token = github_service.get_default_token()
    logger = logging.getLogger("main.list_templates")
    try:
        files = github_service.list_yaml_files(repo, "templates", token=token)
        result = []
        for fname in files:
            try:
                content = github_service.get_file_content(repo, f"templates/{fname}", token=token)
                parsed = template_service.parse_template_file(content)
                result.append({
                    "id": fname,
                    "name": parsed["name"],
                    "description": parsed["description"],
                    "icon": parsed.get("icon"),
                    "repo": repo,
                    "category": parsed.get("category", "")
                })
            except Exception as e:
                logger.error(f"Error procesando plantilla {fname}: {e}", exc_info=True)
        return result
    except Exception as e:
        logger.error(f"Error general al recuperar plantillas: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": str(e)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/template/{template_id}", response_model=TemplateDetail)
def get_template_detail(template_id: str) -> TemplateDetail:
    """
    Devuelve los campos y metadatos de una plantilla específica.
    """
    repo = github_service.get_default_repo()
    token = github_service.get_default_token()
    try:
        content = github_service.get_file_content(repo, f"templates/{template_id}", token=token)
        parsed = template_service.parse_template_file(content)
        return TemplateDetail(
            id=template_id,
            name=parsed["name"],
            description=parsed["description"],
            version=parsed.get("version", ""),
            category=parsed.get("category", ""),
            dependencies=parsed.get("dependencies", []),
            required_networks=parsed.get("required_networks", []),
            tags=parsed.get("tags", []),
            fields=parsed["fields"]
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Plantilla no encontrada: {template_id}. Error: {e}")

@app.post("/generate")
def generate_compose(req: GenerateRequest):
    """
    Genera un docker-compose.yml a partir de una plantilla y valores dados.
    Valida los valores usando las reglas de user_fields de la plantilla.
    """
    from app.services import validation_service  # Import aquí para evitar ciclos
    repo = github_service.get_default_repo()
    token = github_service.get_default_token()
    try:
        content = github_service.get_file_content(repo, f"templates/{req.template_id}", token=token)
        parsed = template_service.parse_template_file(content)
        fields = parsed["fields"]
        # Aplicar defaults antes de validar
        from app.services.template_service import merge_with_defaults
        merged_values = merge_with_defaults(fields, req.values)
        # Validación de campos dinámicos
        validated, errors = validation_service.validate_user_fields(fields, merged_values)
        if errors:
            return JSONResponse(status_code=400, content={"detail": errors})
        # Extraemos el bloque 'template' como string, preservando formato
        from app.services.template_service import extract_template_block, render_template_block
        template_str = extract_template_block(content)
        if not template_str:
            raise HTTPException(status_code=400, detail="No se pudo extraer el bloque 'template' del YAML.")
        # Sustituimos los valores del usuario en el string
        result = render_template_block(template_str, merged_values)
        return JSONResponse(content={"compose": result})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error generando compose: {e}")

from fastapi import Query

@app.get("/download/{template_id}")
def download_compose(template_id: str, request: Request):
    """
    Descarga el docker-compose.yml generado como attachment.
    Los valores para los campos se pasan por query string (?campo1=valor1&campo2=valor2).

    Args:
        template_id (str): Nombre del archivo plantilla YAML.
        request (Request): Objeto request para acceder a query params.

    Returns:
        StreamingResponse: Archivo docker-compose.yml como attachment.
    """
    repo = github_service.get_default_repo()
    token = github_service.get_default_token()
    try:
        content = github_service.get_file_content(repo, f"templates/{template_id}", token=token)
        parsed = template_service.parse_template_file(content)
        yaml_content = parsed["yaml_content"]
        # Extrae todos los query params como dict
        from app.services.template_service import merge_with_defaults
        fields = parsed.get("fields", [])
        values = dict(request.query_params)
        merged_values = merge_with_defaults(fields, values)
        # Usamos directamente el dict extraído de 'template' para evitar problemas de indentación
        result = compose_generator.render_compose_template(parsed["yaml_content_dict"], merged_values)
        return StreamingResponse(
            iter([result]),
            media_type="application/x-yaml",
            headers={"Content-Disposition": "attachment; filename=docker-compose.yml"}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error generando compose para descarga -> {e}")
