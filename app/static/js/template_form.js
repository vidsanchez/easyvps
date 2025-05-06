// template_form.js - Lógica para formulario dinámico EasyVPS

document.addEventListener("DOMContentLoaded", function () {
    const urlParams = new URLSearchParams(window.location.search);
    const templateId = urlParams.get("template_id");
    if (!templateId) {
        mostrarError("No se ha especificado ninguna plantilla.");
        return;
    }
    cargarCampos(templateId);

    document.getElementById("dynamic-form").addEventListener("submit", function(e) {
        e.preventDefault();
        enviarParaPreview(templateId);
    });
});

function cargarCampos(templateId) {
    fetch(`/template/${encodeURIComponent(templateId)}`)
        .then(r => {
            if (!r.ok) throw new Error("No se pudo cargar la plantilla");
            return r.json();
        })
        .then(data => {
            document.querySelector("h1").textContent = `Configurar: ${data.name}`;
            const form = document.getElementById("dynamic-form");
            form.innerHTML = '<div class="form-fields-intro">Complete la siguiente información 👇🏻</div>';
            data.fields.forEach(campo => {
                // Si el campo es un objeto con propiedades, adaptar; si es string, mostrar básico
                let label = campo.label || campo.field || campo;
                let required = campo.required !== false; // Por defecto true si no se especifica
                let description = campo.description || '';
                let type = campo.type || 'text';
                // SVG de requerido
                let requiredSvg = required ? `<svg class='required-indicator' width='9' height='9' viewBox='0 0 9 9'><circle cx='4.5' cy='4.5' r='4.5' fill='#e74c3c'/></svg>` : '';
                const defaultAttr = campo.default !== undefined ? `value='${String(campo.default).replace(/'/g, '&#39;')}'` : '';
                form.innerHTML += `
                  <div class="form-field-block">
                    <label class="form-label">${label}${requiredSvg}</label>
                    <input type='${type}' class='form-control' name='${campo.field || campo}' ${required ? 'required' : ''} ${defaultAttr}>
                    ${description ? `<div class='form-description'>${description}</div>` : ''}
                  </div>`;
            });
            form.innerHTML += `<button class='btn btn-primary' type='submit'>Generar Compose</button>`;
        })
        .catch(err => mostrarError("No se pudo cargar la plantilla: " + err));
}

function enviarParaPreview(templateId) {
    const form = document.getElementById("dynamic-form");
    const formData = new FormData(form);
    const values = {};
    for (const [k,v] of formData.entries()) {
        values[k] = v;
    }
    fetch("/generate", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({template_id: templateId, values})
    })
    .then(r => r.json())
    .then(data => {
        if (data.compose) {
            mostrarPreview(data.compose, templateId, values);
        } else {
            mostrarError("Error generando compose: " + (data.detail || ""));
        }
    })
    .catch(err => mostrarError("Error generando compose: " + err));
}

function mostrarPreview(compose, templateId, values) {
    const previewDiv = document.getElementById("preview");
    previewDiv.innerHTML = `<h3>Preview docker-compose.yml</h3><pre class='bg-light p-3'>${escapeHtml(compose)}</pre>`;
    // Genera url de descarga
    const params = new URLSearchParams(values).toString();
    const url = `/download/${encodeURIComponent(templateId)}?${params}`;
    previewDiv.innerHTML += `<a class='btn btn-success mt-2' href='${url}' download='docker-compose.yml'>Descargar Compose</a>`;
}

function mostrarError(msg) {
    document.getElementById("preview").innerHTML = `<div class='alert alert-danger'>${msg}</div>`;
}

function escapeHtml(text) {
    const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}
