/* ════════════════════════════════════════════════════════════════════ */
/* 🔧 SECCIÓN 1: VARIABLES GLOBALES Y CONFIGURACIÓN                    */
/* ════════════════════════════════════════════════════════════════════ */

let world;                              // 🌍 Instancia del globo 3D
let hoverD = null;                      // 🖱️ Polígono bajo el ratón
let selectedCountry = null;             // 🗺️ Código del país seleccionado
let selectedCountryName = null;         // 🗺️ Nombre del país seleccionado
const BASE_ROTATION_SPEED = 0.5;        // ⚙️ Velocidad de rotación automática
let isConsoleCollapsed = false;         // 📋 Estado de la consola
let isTerminalCollapsed = false;        // 📋 Estado de la terminal

// ── Categorías de noticias ────────────────────────────────────────────
const CATEGORIES = [
    { label: 'GENERAL',        api: '' },
    { label: 'TECNOLOGÍA',     api: 'technology' },
    { label: 'NEGOCIOS',       api: 'business' },
    { label: 'DEPORTES',       api: 'sports' },
    { label: 'ENTRETENIMIENTO',api: 'entertainment' },
    { label: 'SALUD',          api: 'health' },
    { label: 'CIENCIA',        api: 'science' },
];
let currentCatIndex = 0;

function prevCategory() {
    currentCatIndex = (currentCatIndex - 1 + CATEGORIES.length) % CATEGORIES.length;
    updateCategoryUI();
    loadNews(selectedCountry || 'global');
}

function nextCategory() {
    currentCatIndex = (currentCatIndex + 1) % CATEGORIES.length;
    updateCategoryUI();
    loadNews(selectedCountry || 'global');
}

function updateCategoryUI() {
    document.getElementById('cat-label').textContent = CATEGORIES[currentCatIndex].label;
}

// ── Swipe táctil en el selector de categorías ─────────────────────────
let _swipeStartX = null;
document.addEventListener('DOMContentLoaded', () => {
    const catRow = document.querySelector('.category-row');
    if (!catRow) return;
    catRow.addEventListener('touchstart', e => { _swipeStartX = e.touches[0].clientX; }, { passive: true });
    catRow.addEventListener('touchend', e => {
        if (_swipeStartX === null) return;
        const dx = e.changedTouches[0].clientX - _swipeStartX;
        if (Math.abs(dx) > 40) dx < 0 ? nextCategory() : prevCategory();
        _swipeStartX = null;
    }, { passive: true });
});

/* ════════════════════════════════════════════════════════════════════ */
/* 📋 SECCIÓN 2: SISTEMA DE CONSOLA DE ERRORES                        */
/* ════════════════════════════════════════════════════════════════════ */

/**
* ⏰ Genera un timestamp formateado (HH:MM:SS)
* @returns {string} Timestamp en formato HH:MM:SS
*/
function getTimeStamp() {
    const now = new Date();
    return `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`;
}

/**
* 📝 Registra un mensaje en la consola visual
* @param {string} message - Texto del mensaje
* @param {string} type - Tipo: 'error', 'warning', 'success', 'info', 'debug'
* @param {string} details - Detalles adicionales (opcional)
*/
function logToConsole(message, type = 'info', details = '') {
    const timestamp = getTimeStamp();
    
            // 🎯 Mapa de tipos con iconos, etiquetas y clases CSS
    const typeMap = {
        'error': { icon: '🔴', label: 'ERROR', class: 'msg-error' },
        'warning': { icon: '🟡', label: 'WARNING', class: 'msg-warning' },
        'success': { icon: '🟢', label: 'SUCCESS', class: 'msg-success' },
        'info': { icon: '🔵', label: 'INFO', class: 'msg-info' },
        'debug': { icon: '⚫', label: 'DEBUG', class: 'msg-debug' }
    };

            // 📌 Obtener información del tipo, usar 'info' por defecto
    const typeInfo = typeMap[type] || typeMap['info'];
    
            // 🖥️ Registrar en la consola del navegador
    console.log(`[${timestamp}] ${typeInfo.icon} ${typeInfo.label}: ${message}`, details);

            // 🎨 Crear elemento visual para el mensaje
    const msgEl = document.createElement('div');
    msgEl.className = `console-message ${typeInfo.class}`;
    msgEl.innerHTML = `
                <span class="console-time">[${timestamp}]</span>
                <span class="console-type">${typeInfo.icon} ${typeInfo.label}</span>
                <span>${message}</span>
    `;

            // ➕ Agregar mensaje a la consola
    const consoleContent = document.getElementById('console-content');
    consoleContent.appendChild(msgEl);

            // 🔄 Limitar a 50 mensajes (eliminar primero si se excede)
    const messages = consoleContent.querySelectorAll('.console-message');
    if (messages.length > 50) {
        messages[0].remove();
    }

            // 📍 Auto-scroll al final
    consoleContent.scrollTop = consoleContent.scrollHeight;
}

/**
* 🗑️ Limpia todos los mensajes de la consola
*/
function clearConsole() {
    const consoleContent = document.getElementById('console-content');
    consoleContent.innerHTML = '';
    logToConsole('Consola limpiada', 'info');
}

/**
* 🔽 Alterna entre contraer y expandir la terminal de noticias
*/
function toggleTerminal() {
    const box = document.querySelector('.terminal-box');
    const btn = document.querySelector('.terminal-box-btn');
    isTerminalCollapsed = !isTerminalCollapsed;

    if (isTerminalCollapsed) {
        box.classList.add('terminal-box-collapsed');
        btn.textContent = '+';
    } else {
        box.classList.remove('terminal-box-collapsed');
        btn.textContent = '−';
    }
}

/**
* 🔽 Alterna entre contraer y expandir la consola
*/
function toggleConsole() {
    const console = document.getElementById('error-console');
    const btn = document.getElementById('collapse-btn');
    isConsoleCollapsed = !isConsoleCollapsed;
    
    if (isConsoleCollapsed) {
        console.classList.add('console-collapsed');
        btn.textContent = '+';
    } else {
        console.classList.remove('console-collapsed');
        btn.textContent = '−';
    }
}

/* ════════════════════════════════════════════════════════════════════ */
/* 🌍 SECCIÓN 3: INICIALIZACIÓN DEL GLOBO 3D                          */
/* ════════════════════════════════════════════════════════════════════ */

// 🌎 Crear instancia del globo 3D
world = Globe()
(document.getElementById('globeViz'))
            // 🌙 Imagen de la tierra (noche)
.globeImageUrl('//unpkg.com/three-globe/example/img/earth-night.jpg')
            // ⭐ Imagen del cielo/espacio
.backgroundImageUrl('//unpkg.com/three-globe/example/img/night-sky.png')
            // 🎨 Colores y propiedades de los polígonos (países)
.polygonSideColor(() => 'rgba(255, 0, 255, 0.2)')
.polygonStrokeColor(() => '#ff00ff')
            // ✨ Color más brillante al pasar el ratón
.polygonCapColor(d => d === hoverD ? 'rgba(0, 255, 255, 0.3)' : 'rgba(0, 255, 255, 0.00)')
            // 📈 Altura más elevada al pasar el ratón
.polygonAltitude(d => d === hoverD ? 0.05 : 0.00175)
            // 📍 Configurar puntos para territorios pequeños
.pointColor(() => '#ff00ff')
.pointAltitude(0.07)
.pointRadius(0.5)
.pointsMerge(true)
            // 🖱️ Evento: al pasar el ratón sobre un polígono
.onPolygonHover(poly => {
    hoverD = poly;
    world.polygonAltitude(world.polygonAltitude());
})
            // 🖱️ Evento: al hacer clic en un polígono
.onPolygonClick((polygon, event, { lat, lng }) => {
    logToConsole(`🖱️ Polígono clickeado. Inspeccionando propiedades...`, 'debug');

    const d = polygon.properties;
    const name = d.ADMIN || d.name || d.NAME || 'Unknown Country';

    // Natural Earth usa a veces ISO_A2="-99" para territorios especiales;
    // en ese caso intentar campos alternativos antes de caer al nombre.
    let code = d.ISO_A2 || d.iso_a2 || '-99';
    if (code === '-99' || !code) code = d.ISO_A2_EH || '-99';
    if (code === '-99' || !code) code = d.WB_A2     || '-99';
    if (code === '-99' || !code) {
        code = name.toLowerCase().replace(/[\s,.'()]+/g, '_');
        logToConsole(`⚠️ Sin código ISO para "${name}", buscando por nombre`, 'warning');
    }

    selectNode(name, code.toLowerCase(), lat, lng);
})
            // 🖱️ Evento: al hacer clic en un punto (territorio pequeño)
.onPointClick(pt => selectNode(pt.name, pt.id, pt.lat, pt.lng))
            // 🖱️ Evento: al hacer clic en el globo (sin país seleccionado)
.onGlobeClick(() => { if (selectedCountry) resetToGlobal(); });

// Guardar referencia global para la intro
window.myGlobe = world;

// === CONFIGURACIÓN INICIAL LEJANA PARA LA INTRO ===
world.pointOfView({ lat: 25, lng: 0, altitude: 100.0 }, 0); // muy lejos

world.controls().autoRotate = false; // desactivamos rotación al inicio



        // 📏 Ajustar tamaño del globo al redimensionar la ventana
window.addEventListener('resize', (event) => {
    const globeContainer = document.getElementById('globeViz');
    world.width(globeContainer.clientWidth);
    world.height(globeContainer.clientHeight);
});

// 🔄 Activar rotación automática del globo
world.controls().autoRotate = true;
world.controls().autoRotateSpeed = BASE_ROTATION_SPEED;

// 📐 Inclinar el globo para efecto cinemático
const tiltAng = 0.05;  // 📊 Radianes (~3 grados)
world.scene().rotation.z = tiltAng;  // 🔄 Ladeo lateral
world.scene().rotation.x = 0.1;      // 🔄 Inclinación frontal

/* ════════════════════════════════════════════════════════════════════ */
/* 📥 SECCIÓN 4: CARGA DE DATOS GEOGRÁFICOS (GeoJSON)                 */
/* ════════════════════════════════════════════════════════════════════ */

logToConsole('Cargando GeoJSON...', 'info');

        // 📥 Descargar datos de países desde GeoJSON
fetch('https://raw.githubusercontent.com/martynafford/natural-earth-geojson/refs/heads/master/110m/cultural/ne_110m_admin_0_countries_lakes.json')
.then(res => {
    if (!res.ok) throw new Error('No se pudo cargar GeoJSON');
    return res.json();
})

.then(countries => {
                // ✅ Validar estructura del GeoJSON
                // 🔧 PROCESAR Y VALIDAR FEATURES

    // Mantener TODOS los países — los de código -99 se buscan por nombre
    const cleanFeatures = countries.features.filter(f =>
        f.properties &&
        (f.properties.ADMIN || f.properties.name || f.properties.NAME)
    );
                // 📊 Verificar que se cargaron países válidos
    if (cleanFeatures.length === 0) {
        logToConsole('❌ No se encontraron países válidos en el GeoJSON', 'error');
        return;
    }

    logToConsole(`✅ ${cleanFeatures.length} países cargados correctamente`, 'success');

                // 🌍 Cargar datos en el globo
    world.polygonsData(cleanFeatures);
})

.catch(err => {
    logToConsole(`Error cargando GeoJSON: ${err.message}`, 'error');
    console.error('GeoJSON Error:', err);
});

/* ════════════════════════════════════════════════════════════════════ */
/* 🗺️ SECCIÓN 5: FUNCIONES DE INTERACCIÓN CON PAÍSES                  */
/* ════════════════════════════════════════════════════════════════════ */

        /**
         * 🗺️ Selecciona un país y carga sus noticias
         * @param {string} name - Nombre del país
         * @param {string} code - Código ISO del país
         * @param {number} lat - Latitud del centro del país
         * @param {number} lng - Longitud del centro del país
         */
function selectNode(name, code, lat, lng) {
    if (!name || name === 'undefined' || name === '') {
        logToConsole(`❌ Nombre de país inválido (${name})`, 'error');
        return;
    }

    const normalizedCode = String(code || name).toLowerCase().trim();
    logToConsole(`📍 Seleccionando: ${name} (${normalizedCode})`, 'debug');

    selectedCountry = normalizedCode;
    selectedCountryName = name;
    
            // 🎨 Actualizar UI
    document.getElementById('node-label').innerText = `NODE: ${name.toUpperCase()}`;
    document.getElementById('back-button').style.display = 'block';
    
            // 📍 Validar coordenadas
    const validLat = isNaN(lat) ? 0 : lat;
    const validLng = isNaN(lng) ? 0 : lng;
    
            // 📷 Mover cámara a país seleccionado
    world.pointOfView({ lat: validLat, lng: validLng, altitude: 0.6 }, 1000);
    
            // ⚙️ Reducir velocidad de rotación cuando hay país seleccionado
    world.controls().autoRotateSpeed = BASE_ROTATION_SPEED * 0.1;
    
            // 📰 Cargar noticias del país
    loadNews(normalizedCode);
}

/* ════════════════════════════════════════════════════════════════════ */
/* 📰 SECCIÓN 6: FUNCIONES DE NOTICIAS                                */
/* ════════════════════════════════════════════════════════════════════ */

        /**
         * 📥 Carga noticias para un país específico desde la API
         * @param {string} code - Código ISO del país
         */
function loadNews(code) {
    const container = document.getElementById('news-container');
    
            // ✅ Validar código ANTES de hacer la solicitud
    if (!code || code === 'undefined' || code === '' || code === null) {
        logToConsole(`❌ Intento de cargar noticias con código inválido: "${code}"`, 'error');
        container.innerHTML = `
                    <div class="error-box">
                        <strong>❌ CÓDIGO INVÁLIDO</strong><br>
                        Por favor, selecciona un país válido.<br>
                    </div>
        `;
        return;
    }
    
            // ⏳ Mostrar estado de carga
    container.innerHTML = `<div class="status-line">> ACCEDIENDO A SECTOR ${code}...</div>`;
    logToConsole(`Solicitando noticias para: ${code}`, 'info');
    
            // 🔗 Construir URL con categoría activa
    const encodedCode = encodeURIComponent(code);
    const cat = CATEGORIES[currentCatIndex].api;
    const newsUrl = `/country-news?country=${encodedCode}${cat ? '&category=' + cat : ''}`;
    
    logToConsole(`📨 Endpoint: ${newsUrl}`, 'debug');
    
            // 📡 Hacer solicitud al servidor backend
    fetch(newsUrl)
    .then(res => {
        logToConsole(`Status HTTP: ${res.status}`, 'debug');
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
    })
    .then(data => {
                    // ⚠️ Verificar si hay error en la respuesta del servidor
        if (data.status === 'error') {
            logToConsole(`❌ ${data.type}: ${data.message}`, 'error');
            container.innerHTML = `
                            <div class="error-box">
                                <strong>❌ ${data.type}</strong><br>
                                ${data.message}<br>
                                <small>${data.details || ''}</small><br>
                                <button class="retry-btn" onclick="loadNews('${code}')">↻ REINTENTAR</button>
                            </div>
            `;
            return;
        }

                    // 📰 Verificar si hay artículos
        if (data.status === 'warning' || !data.articles || data.articles.length === 0) {
            logToConsole(`⚠️ Sin artículos para ${code}`, 'warning');
            container.innerHTML = `
                            <div class="error-box">
                                <strong>⚠️ SIN RESULTADOS</strong><br>
                                ${data.message}<br>
                                <button class="retry-btn" onclick="loadNews('${code}')">↻ REINTENTAR</button>
                            </div>
            `;
            return;
        }

                    // ✅ Éxito: mostrar artículos
        const articles = data.articles;
        const cacheMsg = data.cached
            ? `⚡ CACHÉ (expira en ${data.expires_in})`
            : '🌐 API (datos frescos)';
        logToConsole(`✅ ${articles.length} noticias para ${code.toUpperCase()} — ${cacheMsg}`, 'success');

                    // 🎨 Limpiar y crear elementos de noticias (solo titular + fuente, sin imagen)
        container.innerHTML = '';
        articles.forEach((art, idx) => {
            const div = document.createElement('div');
            div.className = 'news-item';
            const src = art.source?.name ? `<span class="news-src">${art.source.name}</span>` : '';
            div.innerHTML = `
                <div class="news-item-body">
                    <span class="news-rank">${String(idx + 1).padStart(2, '0')}</span>
                    <span class="news-title-text">${art.title}</span>
                    ${src}
                </div>`;
            div.onclick = () => openReader(art);
            container.appendChild(div);
        });
    })
    .catch(err => {
                    // ❌ Error de conexión
        logToConsole(`🔌 Error de conexión: ${err.message}`, 'error');
        container.innerHTML = `
                        <div class="error-box">
                            <strong>❌ ERROR</strong><br>
                            ${err.message}<br>
                            <button class="retry-btn" onclick="loadNews('${code}')">↻ REINTENTAR</button>
                        </div>
        `;
    });
}

        // ════════════════════════════════════════════════════════════════════
        // 🎨 SECCIÓN 7: FUNCIONES DE INTERFAZ DE USUARIO PANEL DE LECTURA     
        // ════════════════════════════════════════════════════════════════════ 

        /**
         * 📖 Abre el panel de lectura con el contenido completo de un artículo
         * @param {object} article - Objeto del artículo
         */
function openReader(article) {
    const reader = document.getElementById('news-reader');
    const body   = document.getElementById('reader-body');
    reader.classList.add('reader-visible');

    const pubDate    = article.publishedAt
        ? new Date(article.publishedAt).toLocaleDateString('es-ES',
            { day: 'numeric', month: 'short', year: 'numeric' })
        : '';
    const sourceName = article.source?.name || 'FUENTE DESCONOCIDA';

    // Mostrar estructura base con imagen inmediatamente
    const imgHtml = article.urlToImage
        ? `<div class="reader-media-wrap" id="reader-media">
               <img class="reader-image" src="${article.urlToImage}" alt=""
                    onerror="this.style.display='none'">
           </div>`
        : `<div class="reader-media-wrap reader-media-loading" id="reader-media">
               <span class="reader-media-spinner">⟳ BUSCANDO MEDIA...</span>
           </div>`;

    body.innerHTML = `
        ${imgHtml}
        <div class="reader-meta">
            <span class="reader-source">▶ ${sourceName.toUpperCase()}</span>
            ${pubDate ? `<span class="reader-date">${pubDate}</span>` : ''}
        </div>
        <p class="reader-title">${article.title || ''}</p>
        <p class="reader-desc">${article.description || 'Sin resumen disponible.'}</p>
        <a href="${article.url}" target="_blank" class="news-link">[ ACCEDER A FUENTE EXTERNA → ]</a>
    `;

    // Buscar video en la página del artículo de forma asíncrona
    fetch(`/article?url=${encodeURIComponent(article.url)}`)
        .then(r => r.json())
        .then(data => {
            const mediaEl = document.getElementById('reader-media');
            if (!mediaEl) return;
            const v = data.video;
            if (v && v.type === 'youtube' && v.url) {
                // YouTube embed reemplaza la imagen
                mediaEl.innerHTML = `
                    <iframe class="reader-video"
                        src="${v.url}"
                        frameborder="0"
                        allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                        allowfullscreen>
                    </iframe>`;
                mediaEl.classList.remove('reader-media-loading');
                logToConsole('▶ Video de YouTube encontrado y embebido', 'success');
            } else if (v && v.type === 'video' && v.url) {
                // Video nativo HTML5
                mediaEl.innerHTML = `
                    <video class="reader-video" controls preload="metadata">
                        <source src="${v.url}">
                    </video>`;
                mediaEl.classList.remove('reader-media-loading');
                logToConsole('▶ Video HTML5 encontrado', 'success');
            } else if (!article.urlToImage) {
                // Sin video ni imagen
                mediaEl.classList.add('reader-media-empty');
                mediaEl.innerHTML = `<span class="reader-no-media">[ SIN MEDIA DISPONIBLE ]</span>`;
            } else {
                // Ya tiene imagen, no hacer nada
                mediaEl.classList.remove('reader-media-loading');
            }
        })
        .catch(() => {
            const mediaEl = document.getElementById('reader-media');
            if (mediaEl && !article.urlToImage) {
                mediaEl.innerHTML = `<span class="reader-no-media">[ ERROR CARGANDO MEDIA ]</span>`;
            }
        });
}

        /**
         * 🚪 Cierra el panel de lectura
         */
function closeReader() {
    document.getElementById('news-reader').classList.remove('reader-visible');
}

// =======================================
// FUNCION: cargar articulo en visor
// =======================================
function loadArticle(url) {

    const viewer = document.getElementById("articleViewer");

    // Mostrar visor + loading
    viewer.style.display = "block";
    viewer.innerHTML = "Cargando artículo...";

    // Llamada a Flask
    fetch(`/article?url=${encodeURIComponent(url)}`)
    .then(res => res.json())
    .then(data => {

            // Renderizamos contenido
        viewer.innerHTML = `
                <h2 style="color:#00ffff;">${data.title}</h2>
                <hr>
                <p style="white-space: pre-line;">
                    ${data.content}
                </p>

                <br>
                <a href="${url}" target="_blank" style="color:#ff00ff;">
                    🔗 Ver original
                </a>
        `;
    })
    .catch(err => {
        viewer.innerHTML = "Error cargando artículo";
        console.error(err);
    });
}

        /* ════════════════════════════════════════════════════════════════════ */
        /* 🚀 SECCIÓN 8: INICIALIZACIÓN DE LA APLICACIÓN                      */
        /* ════════════════════════════════════════════════════════════════════ */

        /**
         * � Resetea la vista al globo global y carga noticias mundiales
         */
function resetToGlobal() {
    logToConsole('Reseteando a vista global', 'info');
    selectedCountry = null;
    closeReader();
    document.getElementById('node-label').innerText = `NODE: GLOBAL FEED`;
    document.getElementById('back-button').style.display = 'none';
    world.pointOfView({ lat: 20, lng: 0, altitude: 1.5 }, 1000);
    world.controls().autoRotateSpeed = BASE_ROTATION_SPEED;
    loadNews('global');
}

        /**
         * 🚀 Ejecuta al cargar la página completa
         */
window.onload = () => {
    logToConsole('Aplicación cargada', 'success');
    
    initIntro();           // ← Nueva línea
    // resetToGlobal();    // se llamará automáticamente después del click
};