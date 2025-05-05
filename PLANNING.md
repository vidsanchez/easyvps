# PLANNING.md

## EasyVPS SaaS - MVP Simplificado

### Objetivo
Crear una aplicación web que genere formularios dinámicos a partir de plantillas Docker Compose y permita descargar/copiar la configuración generada para usar en Portainer.

### Flujo de Usuario
1. Usuario accede a la aplicación
2. Sistema descarga plantillas desde GitHub (primera vez)
3. Usuario selecciona una plantilla
4. Sistema genera formulario dinámico basado en campos `[[field]]`
5. Usuario completa el formulario
6. Sistema genera docker-compose.yml configurado
7. Usuario descarga/copia el archivo para usar en Portainer

### Arquitectura Simplificada

**Backend (Python)**
- Framework: FastAPI
- Sin base de datos
- Sin autenticación
- Cache temporal de plantillas en memoria

**Frontend**
- HTML/JavaScript puro (Formularios dinámicos)
- Bootstrap o Tailwind para estilos
- Integrado en FastAPI con templates Jinja2

### Estructura de Datos

**Template Processing**
```python
{
    'name': 'Redis',
    'description': 'Plantilla para Redis',
    'fields': ['username', 'password', 'subdominio'],
    'yaml_content': '...'
}
```

### Componentes Clave

1. **GitHub Fetcher**: Descarga plantillas al iniciar
2. **Form Generator**: Crea formularios HTML dinámicamente
3. **YAML Processor**: Reemplaza placeholders y genera compose
4. **Download Handler**: Sirve el archivo generado

### Tecnologías
- FastAPI + Uvicorn
- PyYAML para parsear templates
- Requests para GitHub API
- Jinja2 para templates HTML
- Bootstrap para interfaz

### Flujo de Datos
```
GitHub Repo → Cache en memoria → Selección → Form → Configuración → Docker Compose
```

### MVP Features
- [x] Descarga automática de plantillas
- [x] Generación de formularios dinámicos
- [x] Parseo de campos [[variable]]
- [x] Generación de docker-compose.yml
- [x] Botón de descarga del compose generado