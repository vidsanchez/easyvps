// formulario_inline.js - Renderiza un formulario dinámico tipo acordeón debajo de la card seleccionada

export function renderFormularioInline(cardElem, templateId, templateName) {
    // Elimina cualquier modal abierto previamente
    document.querySelectorAll('.modal-backdrop-easyvps, .modal-easyvps').forEach(e => e.remove());

    // Fondo difuminado
    const backdrop = document.createElement('div');
    backdrop.className = 'modal-backdrop-easyvps';
    document.body.appendChild(backdrop);
    document.body.classList.add('modal-open');

    // Modal centrado
    const modal = document.createElement('div');
    modal.className = 'modal-easyvps';
    modal.innerHTML = `
      <div class='modal-content-easyvps'>
        <button class='modal-close-easyvps' title='Cerrar'>&times;</button>

        <form class='dynamic-form'></form>
        <div class='inline-preview mt-3'></div>
      </div>
    `;
    document.body.appendChild(modal);

    // Cierre modal
    const closeModal = () => {
      modal.remove();
      backdrop.remove();
      document.body.classList.remove('modal-open');
      document.removeEventListener('keydown', escListener);
    };

    backdrop.addEventListener('click', closeModal);
    modal.querySelector('.modal-close-easyvps').addEventListener('click', closeModal);
    const escListener = (e) => { if (e.key === 'Escape') closeModal(); };
    document.addEventListener('keydown', escListener);

    // Cargar campos
    fetch(`/template/${encodeURIComponent(templateId)}`)
      .then(r => { if (!r.ok) throw new Error("No se pudo cargar la plantilla"); return r.json(); })
      .then(data => {
        // Cabecera avanzada del modal
        const modalHeader = document.createElement('div');
        modalHeader.className = 'modal-header-easyvps mb-3';
        modalHeader.innerHTML = `
          <h2 class='modal-title-easyvps mb-2'>${data.name}</h2>
          <div class='modal-meta-easyvps mb-2'>
            <span class='badge badge-category'>${data.category || 'Sin categoría'}</span>
            <span class='badge badge-version'>v${data.version || '1.0'}</span>
            ${data.tags && data.tags.length ? data.tags.map(t=>`<span class='badge badge-tag'>${t}</span>`).join('') : ''}
          </div>
          <div class='modal-desc-easyvps mb-2'>${data.description || ''}</div>
          <div class='modal-deps-nets-row mb-2'>
            <div class='modal-deps-easyvps'>
              ${data.dependencies && data.dependencies.length ? `<b>Dependencias:</b> ${data.dependencies.map(dep=>`<span class='badge badge-dep'>${dep}</span>`).join(' ')}` : ''}
            </div>
            <div class='modal-nets-easyvps'>
              ${data.required_networks && data.required_networks.length ? `<b>Redes requeridas:</b> ${data.required_networks.map(n=>`<span class='badge badge-net'>${n}</span>`).join(' ')}` : ''}
            </div>
          </div>
        `;
        modal.querySelector('.modal-content-easyvps').insertBefore(modalHeader, modal.querySelector('form'));
        // Formulario
        const form = modal.querySelector('.dynamic-form');
        form.innerHTML = '<div class="form-fields-intro">Complete la siguiente información 👇🏻</div>';
        // Ordenar campos: usuario, password, subdominio, luego avanzados
        const userFields = ['usuario', 'user', 'username'];
        const passFields = ['password', 'pass'];
        const subdomFields = ['subdominio', 'subdomain'];
        let user = null, pass = null, subdom = null, avanzados = [];
        data.fields.forEach(campo => {
          const key = campo.field.toLowerCase();
          if (userFields.includes(key)) user = campo;
          else if (passFields.includes(key)) pass = campo;
          else if (subdomFields.includes(key)) subdom = campo;
          else avanzados.push(campo);
        });
        const renderCampo = (campo) => {
          const label = campo.label || campo.field;
          const type = campo.type === 'password' ? 'text' : (campo.type || 'text');
          const required = campo.required ? 'required' : '';
          let inputHtml = '';
          if (campo.type === 'password') {
            inputHtml = `
              <div class='input-group'>
                <input type='text' class='form-control' name='${campo.field}' autocomplete='new-password' ${required} />
                <button type='button' class='btn btn-outline-secondary btn-genpass' tabindex='-1' title='Generar contraseña'>&#128273;</button>
              </div>
            `;
          } else {
            inputHtml = `<input type='${type}' class='form-control' name='${campo.field}' ${required} />`;
          }
          return `
            <div class="form-field-block">
              <label class="form-label">${label}${campo.required ? `<svg class='required-indicator' width='9' height='9' viewBox='0 0 9 9'><circle cx='4.5' cy='4.5' r='4.5' fill='#e74c3c'/></svg>` : ''}</label>
              ${inputHtml}
              ${campo.description ? `<div class='form-description'>${campo.description}</div>` : ''}
            </div>`;
        };

        if (user) form.innerHTML += renderCampo(user);
        if (pass) form.innerHTML += renderCampo(pass);
        if (subdom) form.innerHTML += renderCampo(subdom);
        if (avanzados.length) {
          form.innerHTML += `<div class='mb-2 mt-2'><b>Configuración avanzada</b></div>`;
          avanzados.forEach(campo => { form.innerHTML += renderCampo(campo); });
        }
        form.innerHTML += `<button type='submit' class='btn btn-primary'>Generar Compose</button>`;
        // --- Sincronización de password con cookie ---
        // Funciones auxiliares para cookies
        function setCookie(name, value, days) {
          let expires = '';
          if (days) {
            const date = new Date();
            date.setTime(date.getTime() + (days*24*60*60*1000));
            expires = '; expires=' + date.toUTCString();
          }
          document.cookie = name + '=' + encodeURIComponent(value) + expires + '; path=/';
        }
        function getCookie(name) {
          const v = document.cookie.match('(^|;) ?' + name + '=([^;]*)(;|$)');
          return v ? decodeURIComponent(v[2]) : null;
        }
        // Si hay cookie, pre-rellena el campo password
        const passInput = form.querySelector('.input-group input[name="password"]');
        if (passInput) {
          const cookiePass = getCookie('easyvps_password');
          if (cookiePass) passInput.value = cookiePass;
          // Guarda la cookie al cambiar
          passInput.addEventListener('input', () => {
            setCookie('easyvps_password', passInput.value, 90);
          });
        }
        // Lógica generación password
        form.querySelectorAll('.btn-genpass').forEach(btn => {
          btn.addEventListener('click', function() {
            const input = this.closest('.input-group').querySelector('input');
            input.value = generarPasswordBonita();
            // Guarda la nueva password en cookie
            if (input.name === 'password') {
              setCookie('easyvps_password', input.value, 90);
            }
          });
        });
        form.addEventListener('submit', function(e) {
          e.preventDefault();
          enviarParaPreview(templateId, form, modal.querySelector('.inline-preview'));
        });
      })
      .catch(err => {
        modal.querySelector('.dynamic-form').innerHTML = `<div class='alert alert-danger'>Error: ${err.message}</div>`;
      });
}

function generarPasswordBonita() {
  // Genera una contraseña segura de 16 caracteres (letras, números y símbolos)
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789!#$%';
  let pass = '';
  for (let i = 0; i < 16; i++) pass += chars[Math.floor(Math.random() * chars.length)];
  return pass;
}


function enviarParaPreview(templateId, form, previewDiv) {
    const formData = new FormData(form);
    const values = {};
    for (const [k,v] of formData.entries()) values[k] = v;
    previewDiv.innerHTML = `<div class='loading-message'><span class='spinner'></span><br>Generando compose...</div>`;
    fetch("/generate", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({template_id: templateId, values})
    })
    .then(r => r.json())
    .then(data => {
        if (data.compose) {
            mostrarPreview(data.compose, templateId, values, previewDiv);
        } else {
            mostrarError("Error generando compose: " + (data.detail || ""), previewDiv);
        }
    })
    .catch(err => mostrarError("Error generando compose: " + err, previewDiv));
}

function mostrarPreview(compose, templateId, values, previewDiv) {
    previewDiv.innerHTML = `<h6>Preview docker-compose.yml</h6><pre class='bg-light p-3'>${escapeHtml(compose)}</pre>`;
    const params = new URLSearchParams(values).toString();
    const url = `/download/${encodeURIComponent(templateId)}?${params}`;
    previewDiv.innerHTML += `<a class='btn btn-success mt-2' href='${url}' download='docker-compose.yml'>Descargar Compose</a>`;
}

function mostrarError(msg, previewDiv) {
    previewDiv.innerHTML = `<div class='alert alert-danger'>${msg}</div>`;
}

function escapeHtml(text) {
    const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}
