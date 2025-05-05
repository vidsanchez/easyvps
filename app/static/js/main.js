// main.js - Lógica frontend para EasyVPS

document.addEventListener("DOMContentLoaded", function () {
    cargarPlantillas();
});

let plantillasData = [];

function cargarPlantillas() {
    const grid = document.getElementById("plantillas-grid");
    grid.innerHTML = '<div class="loading-message"><span class="spinner"></span><br>Cargando plantillas, por favor espera...</div>';
    fetch("/templates")
        .then(r => {
            if (!r.ok) throw new Error("No se pudieron recuperar las plantillas");
            console.log("Plantillas recuperadas:", r);
            return r.json();
        })
        .then(plantillas => {
            plantillasData = plantillas;
            renderizarPlantillas(plantillas);
            const search = document.getElementById("search-bar");
            search.addEventListener("input", function() {
                const q = search.value.trim().toLowerCase();
                const filtradas = plantillasData.filter(p =>
                    (p.name && p.name.toLowerCase().includes(q)) ||
                    (p.description && p.description.toLowerCase().includes(q))
                );
                renderizarPlantillas(filtradas);
            });
        })
        .catch(err => {
            grid.innerHTML = `<div class='loading-message text-danger'>Error: ${err.message}</div>`;
        });
}

function renderizarPlantillas(plantillas) {
    const grid = document.getElementById("plantillas-grid");
    grid.innerHTML = "";
    if (plantillas.length === 0) {
        grid.innerHTML = '<div class="text-center w-100 text-muted">No templates found</div>';
        return;
    }
    plantillas.forEach(p => {
        const card = document.createElement("div");
        card.className = "card-template";
        // Construir URL del icono de GitHub si existe, si no usar icono por defecto
        let iconUrl = "/static/icons/default.svg";
        console.log("Icono:", p.name, ' -> ', p.icon);
        if (p.icon && p.icon !== "" && p.repo && p.repo.includes("/")) {
            const [owner, repo] = p.repo.split("/");
            iconUrl = `https://raw.githubusercontent.com/${owner}/${repo}/main/icons/${p.icon}`;
        }
        // Debug: mostrar la URL del icono en consola
        // console.log("Icono para", p.name, "->", iconUrl);
        card.innerHTML = `
            <img class="template-icon" src="${iconUrl}" alt="icono ${p.name}" title="${iconUrl}" />
            <div class="template-title">${p.name}</div>
            <div class="template-desc">${p.description}</div>
            <div class="template-card-bottom" style="display:flex;align-items:center;justify-content:space-between;width:100%;margin-top:1.2em;">
                <span class="template-category" style="color:#ffd600;font-weight:600;font-size:1.04em;">${p.category || ''}</span>
                <button class="template-btn">Seleccionar</button>
            </div>
        `;
        // Añadir fallback y tooltip dinámico si falla la imagen
        const img = card.querySelector('.template-icon');
        img.onerror = function() {
            this.onerror = null;
            this.src = '/static/icons/default.svg';
            this.title = 'No se pudo cargar el icono personalizado. Mostrando icono por defecto.';
        };

        // Añadir event listener al botón
        const btn = card.querySelector('.template-btn');
        btn.addEventListener('click', () => {
            renderFormularioInline(card, p.id, p.name);
        });
        grid.appendChild(card);
    });
}

import { renderFormularioInline } from './formulario_inline.js';

function seleccionarPlantilla(templateId) {
    // Busca la card correspondiente
    const grid = document.getElementById('plantillas-grid');
    const cards = Array.from(grid.getElementsByClassName('card-template'));
    const idx = plantillasData.findIndex(p => p.id === templateId);
    if (idx === -1) return;
    const cardElem = cards[idx];
    renderFormularioInline(cardElem, templateId, plantillasData[idx].name);
}
