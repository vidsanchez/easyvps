# TASK.md

## Tareas MVP - EasyVPS SaaS

### 1. Configuración Inicial
- [x] Crear archivo de requerimientos
- [x] Crear estructura básica de directorios:
  ```
  /app
    ├── main.py
    ├── templates/
    │   ├── index.html
    │   └── template_form.html
    ├── static/
    │   └── css/
    └── services/
        ├── github_service.py
        ├── template_service.py
        └── compose_generator.py
  ```
- [x] Crear archivo `.env.example` con `GITHUB_TOKEN`

### 2. Backend - Servicios Core

**GitHub Service**
- [x] Implementar función para descargar archivos del repositorio
- [x] Crear función para parsear archivos YAML
- [x] Implementar cache simple en memoria de plantillas

**Template Service**
- [x] Extraer campos `[[variable]]` de plantillas
- [x] Generar esquema de formulario dinámico (estructura base)
- [ ] Validar plantilla y dependencias

**Compose Generator**
- [x] Crear función para reemplazar placeholders
- [x] Generar docker-compose.yml final
- [ ] Manejar dependencias básicas

### 3. Backend - Endpoints FastAPI

- [ ] `/` - Página principal con lista de plantillas
- [ ] `/template/{template_id}` - Formulario para plantilla específica
- [ ] `/generate` - POST para generar compose
- [ ] `/download/{session_id}` - Descargar compose generado

### 4. Frontend - Templates HTML

**index.html**
- [x] Lista de plantillas disponibles
- [x] Descripción básica de cada plantilla
- [x] Botón para seleccionar plantilla

**template_form.html**
- [x] Renderizado dinámico de campos
- [x] Validación básica de formulario
- [x] Botón submit para generar compose
- [x] Área de preview/descarga

### 5. Integración

- [x] Integrar servicios en endpoints FastAPI usando get_default_repo y get_default_token
- [x] Endpoint `/template/{template_id}`: devuelve campos y metadatos de la plantilla
- [x] Endpoint `/generate`: genera y devuelve el compose con los valores recibidos
- [x] Endpoint `/download/{session_id}`: descarga del compose generado (MVP: `/download/{template_id}` con valores por query string)
    - [x] Test Pytest para endpoint `/download/{template_id}`
    - [x] Tests Pytest para endpoints `/templates`, `/template/{template_id}`, `/generate`
    - [x] Validación de integración real (con repo privado y token, flujo completo probado OK)

---
#### Descubierto Durante el Trabajo
- [ ] Centralizar configuración de repo/token vía funciones utilitarias en github_service
- [ ] Añadir tests manuales y utilitarios para debugging real de integración con GitHub privado

**Docker Setup**
- [ ] Crear Dockerfile simple
- [ ] Crear docker-compose.yml para desarrollo
- [ ] Configurar variables de entorno

**Testing Básico**
- [ ] Probar descarga de plantillas
- [ ] Verificar generación de formularios
- [ ] Validar output del docker-compose

### 6. Deployment

- [ ] Preparar para despliegue en Portainer
- [ ] Documentar URLs y puertos necesarios
- [ ] Crear README básico

## Prioridad de Ejecución

### Semana 1
1. Configurar entorno y estructura
2. Implementar GitHub service básico
3. Crear parser de plantillas

### Semana 2
1. Desarrollar generador de formularios
2. Implementar endpoints básicos
3. Crear templates HTML

### Semana 3
1. Implementar generación de compose
2. Testing integral
3. Preparar para despliegue

## Notas Importantes

- Usar cache simple en memoria (dict o dataclass)
- No implementar autenticación ni sesiones
- Formularios HTML puros con validación básica
- Focus en funcionalidad sobre UX avanzada
- Seguir convenciones FastAPI estándar