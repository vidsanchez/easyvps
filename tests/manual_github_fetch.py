"""
Script manual para probar la recuperación de plantillas YAML desde GitHub.
Edita las variables REPO y PATH según tu repo/estructura.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.services import github_service, template_service

def main():
    # Configura aquí tu repo y path
    REPO = "vidsanchez/easyvps.templates"  # Ejemplo: "owner/repo"
    PATH = "templates"  # Ejemplo: carpeta donde están los YAML
    TOKEN = os.getenv("GITHUB_TOKEN")

    print(f"Listando archivos YAML en {REPO}/{PATH}...")
    files = github_service.list_yaml_files(REPO, PATH, token=TOKEN)
    print(f"Archivos encontrados: {files}")

    if not files:
        print("No se encontraron archivos YAML.")
        return

    # Descarga y muestra el contenido del primer archivo
    fname = files[0]
    print(f"\nDescargando y mostrando '{fname}':\n")
    content = github_service.get_file_content(REPO, f"{PATH}/{fname}", token=TOKEN)
    print(content[:500])  # Solo primeros 500 chars

    # Parsear como plantilla
    parsed = template_service.parse_template_file(content)
    print("\nResumen parseado:")
    print(parsed)

if __name__ == "__main__":
    main()
